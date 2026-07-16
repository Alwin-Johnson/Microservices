"""
Structured JSON logging middleware.

Framework agnostic: exposes a `RequestLogger` class with explicit
on_request_start / on_request_complete / on_retry / on_error hooks, plus
a ready-made Flask adapter so gateway/orders/payments/inventory can
attach logging in one line at app-startup, without touching route
handlers or business logic.

Log line schema (one JSON object per line, written to
environment/logs/<service>.log -- created at runtime, not checked in):

{
  "ts": "2026-07-16T10:00:00",
  "service": "orders",
  "correlation_id": "a1b2c3...",
  "event": "request_start" | "request_complete" | "retry" | "error",
  "method": "POST",
  "path": "/orders",
  "status": 200,
  "duration_ms": 12.4,
  "attempt": 1,
  "reason": "timeout",
  "error": "..."
}
"""
import json
import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from services.shared.tracing.correlation import extract_or_create, get_correlation_id

DEFAULT_LOG_DIR = "environment/logs"


def _build_logger(service_name: str, log_dir: str = DEFAULT_LOG_DIR) -> logging.Logger:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"svc.{service_name}")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        f"{log_dir}/{service_name}.log", maxBytes=20_000_000, backupCount=3
    )
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger


class RequestLogger:
    def __init__(self, service_name: str, log_dir: str = DEFAULT_LOG_DIR):
        self.service_name = service_name
        self.logger = _build_logger(service_name, log_dir)

    def _emit(self, event: str, **fields):
        record = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "service": self.service_name,
            "correlation_id": get_correlation_id(),
            "event": event,
        }
        record.update(fields)
        self.logger.info(json.dumps(record))

    def on_request_start(self, method: str, path: str, headers: dict):
        extract_or_create(headers)
        self._emit("request_start", method=method, path=path)
        return time.perf_counter()

    def on_request_complete(self, method, path, status, start_time, **extra):
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        self._emit(
            "request_complete",
            method=method,
            path=path,
            status=status,
            duration_ms=duration_ms,
            **extra,
        )

    def on_retry(self, method, path, attempt, reason):
        self._emit("retry", method=method, path=path, attempt=attempt, reason=reason)

    def on_error(self, method, path, error):
        self._emit("error", method=method, path=path, error=str(error))


def flask_logging_middleware(app, service_name: str, log_dir: str = DEFAULT_LOG_DIR):
    """Attach structured request logging to a Flask app. Call once at
    app-factory time:

        from services.shared.logger import flask_logging_middleware
        flask_logging_middleware(app, "orders")
    """
    from flask import g, request

    rl = RequestLogger(service_name, log_dir)

    @app.before_request
    def _before():
        g._rl_start = rl.on_request_start(request.method, request.path, dict(request.headers))

    @app.after_request
    def _after(response):
        rl.on_request_complete(
            request.method,
            request.path,
            response.status_code,
            g.get("_rl_start", time.perf_counter()),
        )
        return response

    return rl
