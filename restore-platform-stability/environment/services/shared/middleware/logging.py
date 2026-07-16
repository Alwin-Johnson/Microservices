import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from shared.logger.custom_logger import setup_logger

logger = setup_logger("request_logger")

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses."""
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - Duration: {process_time:.4f}s"
        )
        return response
