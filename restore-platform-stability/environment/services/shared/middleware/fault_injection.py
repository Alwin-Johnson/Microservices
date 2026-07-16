"""
Fault injection layer -- turns the healthy application into a
realistic, replay-triggered incident without editing any business
logic in services/gateway|orders|payments|inventory.

Design goals (per the incident-team brief):
  - The baseline workload must pass through completely unaffected.
  - Only sustained load (the failure/hidden replay) trips the fault,
    and only after several seconds of elevated request rate -- there
    is no single request or log line that reveals the bug outright.
  - The fault must look and behave like a genuine resource-exhaustion /
    retry-amplification incident: a bounded pool of "slots" that a
    request must acquire before being handled. Under sustained
    concurrent load, a fraction of slot releases silently leak (never
    actually free capacity), so p99 latency and 503s climb over the
    course of the burst and only recover once load drops long enough
    for the background reaper to reclaim the leaked slots.
  - A decoy signal (a synthetic CPU-saturation gauge that also rises
    under load) is exposed alongside the real one, so there is more
    than one lead to investigate and rule out.
  - Applied as WSGI middleware in `install()`, wrapping whatever Flask
    app each service already exposes. Never imports or edits any
    services/<name> business logic, only observes and gates traffic in
    front of it.

Environment variables (all optional, sensible defaults below):
  FAULT_MODE               "on" / "off" (default "off")
  FAULT_POOL_SIZE          simulated slot pool size (default 24)
  FAULT_LEAK_RATE          fraction of releases that leak once tripped (default 0.12)
  FAULT_WINDOW_SECONDS     sliding window used to measure request rate (default 10)
  FAULT_TRIP_RPS           requests/window above which leaking begins (default 18)
  FAULT_REAPER_INTERVAL    seconds between background reclaim passes (default 45)
"""
import os
import random
import threading
import time

from prometheus_client import Gauge

FAULT_ENABLED = os.environ.get("FAULT_MODE", "off") == "on"

SLOT_POOL_SIZE = int(os.environ.get("FAULT_POOL_SIZE", "24"))
LEAK_RATE = float(os.environ.get("FAULT_LEAK_RATE", "0.12"))
WINDOW_SECONDS = float(os.environ.get("FAULT_WINDOW_SECONDS", "10"))
TRIP_REQUESTS_PER_WINDOW = int(os.environ.get("FAULT_TRIP_RPS", "18"))
REAPER_INTERVAL_SECONDS = float(os.environ.get("FAULT_REAPER_INTERVAL", "45"))

SIM_POOL_IN_USE = Gauge(
    "sim_pool_slots_in_use", "Simulated resource-pool slots currently held", ["service"]
)
SIM_POOL_LEAKED = Gauge(
    "sim_pool_slots_leaked", "Simulated resource-pool slots leaked (never released)", ["service"]
)
DECOY_CPU_SATURATION = Gauge(
    "cpu_saturation_ratio", "Synthetic CPU saturation signal (decoy, not the root cause)", ["service"]
)


class _SlotPool:
    """Bounded pool of slots that leaks under sustained load past a
    request-rate threshold, and self-heals slowly via a reaper thread.
    This is the actual root cause of the seeded incident."""

    def __init__(self, service_name: str, size: int = SLOT_POOL_SIZE):
        self.service_name = service_name
        self.size = size
        self.in_use = 0
        self.leaked = 0
        self._lock = threading.Lock()
        self._recent_requests = []
        self._start_reaper()

    def _start_reaper(self):
        def _reap():
            while True:
                time.sleep(REAPER_INTERVAL_SECONDS)
                with self._lock:
                    if self.leaked > 0:
                        reclaim = max(1, self.leaked // 3)
                        self.leaked -= reclaim
                        self.in_use = max(0, self.in_use - reclaim)
                        SIM_POOL_IN_USE.labels(self.service_name).set(self.in_use)
                        SIM_POOL_LEAKED.labels(self.service_name).set(self.leaked)

        t = threading.Thread(target=_reap, daemon=True)
        t.start()

    def _current_rate(self) -> int:
        now = time.time()
        self._recent_requests = [t for t in self._recent_requests if now - t <= WINDOW_SECONDS]
        return len(self._recent_requests)

    def acquire(self) -> bool:
        with self._lock:
            self._recent_requests.append(time.time())
            rate = self._current_rate()
            DECOY_CPU_SATURATION.labels(self.service_name).set(min(0.99, 0.2 + rate / 100.0))

            if self.in_use >= self.size:
                return False

            self.in_use += 1
            SIM_POOL_IN_USE.labels(self.service_name).set(self.in_use)
            SIM_POOL_LEAKED.labels(self.service_name).set(self.leaked)

            if rate > TRIP_REQUESTS_PER_WINDOW and random.random() < LEAK_RATE:
                self.leaked += 1
            return True

    def release(self):
        with self._lock:
            if self.leaked > 0:
                # A leaked slot "pretends" to release but never actually
                # frees capacity -- this is the bug. Decrementing leaked
                # here would hide it, so we deliberately don't.
                return
            self.in_use = max(0, self.in_use - 1)
            SIM_POOL_IN_USE.labels(self.service_name).set(self.in_use)


_pools = {}
_pools_lock = threading.Lock()


def _get_pool(service_name: str) -> _SlotPool:
    with _pools_lock:
        if service_name not in _pools:
            _pools[service_name] = _SlotPool(service_name)
        return _pools[service_name]


class ChaosMiddleware:
    """WSGI middleware: acquire a simulated slot before passing the
    request through to the real app, release it after. Returns 503
    when the pool is exhausted so the gateway's existing retry logic
    (owned by the application team, untouched here) naturally amplifies
    load under the failure replay -- exactly like a real production
    incident."""

    def __init__(self, app, service_name: str):
        self.app = app
        self.service_name = service_name
        self.pool = _get_pool(service_name)

    def __call__(self, environ, start_response):
        if not FAULT_ENABLED:
            return self.app(environ, start_response)

        if not self.pool.acquire():
            body = b'{"error": "temporarily unavailable"}'
            start_response(
                "503 Service Unavailable",
                [("Content-Type", "application/json"), ("Content-Length", str(len(body)))],
            )
            return [body]

        try:
            return self.app(environ, start_response)
        finally:
            self.pool.release()


def install(flask_app, service_name: str):
    """Wrap a Flask app's WSGI callable in the chaos middleware. Call
    once at service startup -- no route or business-logic changes:

        from services.shared.middleware import install as install_fault_injection
        install_fault_injection(app, "gateway")
    """
    flask_app.wsgi_app = ChaosMiddleware(flask_app.wsgi_app, service_name)
    return flask_app
