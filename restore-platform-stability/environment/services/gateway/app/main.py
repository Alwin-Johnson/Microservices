from fastapi import FastAPI
from app.api.health import router as health_router
from shared.config.settings import settings
from shared.db.session import SessionLocal
from shared.redis.client import get_redis
from shared.logger.custom_logger import setup_logger
from shared.middleware.logging import LoggingMiddleware
from shared.errors.exceptions import PlatformError
from shared.utils.http_client import get_http_client
from shared.utils.common import format_response

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Gateway Service")
    app.include_router(health_router)
    from app.api.proxy import router as proxy_router
    app.include_router(proxy_router)
    from app.api.checkout import router as checkout_router
    app.include_router(checkout_router)
    return app

app = create_app()
