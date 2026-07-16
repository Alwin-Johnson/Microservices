"""
Prometheus metrics middleware.

Exposes standard RED metrics (Rate, Errors, Duration) plus retry and
connection-pool gauges -- exactly the signals an investigator needs to
correlate logs with metrics during the seeded incident. Attach at
app-startup time only; no business logic changes required.
"""
import time

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["service", "method", "path", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency",
    ["service", "method", "path"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)
RETRY_COUNT = Counter(
    "http_retries_total", "Total retries issued", ["service", "path", "reason"]
)
POOL_IN_USE = Gauge(
    "db_pool_connections_in_use", "DB connections currently checked out", ["service"]
)
POOL_SIZE = Gauge(
    "db_pool_connections_total", "DB connection pool size", ["service"]
)


class MetricsRecorder:
    def __init__(self, service_name: str):
        self.service_name = service_name

    def start_timer(self):
        return time.perf_counter()

    def record_request(self, method, path, status, start_time):
        duration = time.perf_counter() - start_time
        REQUEST_COUNT.labels(self.service_name, method, path, str(status)).inc()
        REQUEST_LATENCY.labels(self.service_name, method, path).observe(duration)

    def record_retry(self, path, reason="timeout"):
        RETRY_COUNT.labels(self.service_name, path, reason).inc()

    def set_pool_stats(self, in_use: int, size: int):
        POOL_IN_USE.labels(self.service_name).set(in_use)
        POOL_SIZE.labels(self.service_name).set(size)


def flask_metrics_middleware(app, service_name: str):
    """Attach RED metrics + a /metrics scrape endpoint to a Flask app:

        from services.shared.metrics import flask_metrics_middleware
        flask_metrics_middleware(app, "orders")
    """
    from flask import Response, g, request

    recorder = MetricsRecorder(service_name)

    @app.before_request
    def _before():
        g._metrics_start = recorder.start_timer()

    @app.after_request
    def _after(response):
        recorder.record_request(
            request.method,
            request.path,
            response.status_code,
            g.get("_metrics_start", time.perf_counter()),
        )
        return response

    @app.route("/metrics")
    def _metrics():
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    return recorder
