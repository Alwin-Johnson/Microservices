import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from shared.logger.custom_logger import setup_logger
from shared.logger.context import set_correlation_id, set_request_id
from shared.metrics.prometheus import REQUEST_COUNT, REQUEST_LATENCY, ERROR_COUNT

logger = setup_logger("http_request")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests, propagating IDs, and recording metrics."""

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path == "/metrics":
            return await call_next(request)

        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request_id = str(uuid.uuid4())

        set_correlation_id(correlation_id)
        set_request_id(request_id)

        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={"extra_info": {"method": request.method, "path": request.url.path}},
        )

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            process_time = time.perf_counter() - start_time

            # Record metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=str(response.status_code),
            ).inc()

            REQUEST_LATENCY.labels(
                method=request.method, endpoint=request.url.path
            ).observe(process_time)

            logger.info(
                f"Request completed: {request.method} {request.url.path} with status {response.status_code}",
                extra={
                    "extra_info": {
                        "status_code": response.status_code,
                        "duration_s": round(process_time, 4),
                    }
                },
            )

            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            process_time = time.perf_counter() - start_time

            ERROR_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                error_type=type(e).__name__,
            ).inc()

            # Count 500s inherently in the error catch block
            REQUEST_COUNT.labels(
                method=request.method, endpoint=request.url.path, status_code="500"
            ).inc()

            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "extra_info": {
                        "error": str(e),
                        "duration_s": round(process_time, 4),
                    }
                },
                exc_info=True,
            )
            raise
