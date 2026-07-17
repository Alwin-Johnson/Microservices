from fastapi import FastAPI
from contextlib import asynccontextmanager
from shared.logger.custom_logger import setup_logger
from shared.middleware.logging import LoggingMiddleware
from app.api.health import router as health_router

logger = setup_logger("gateway")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Service starting up...")
    yield
    logger.info("Service shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Gateway Service", lifespan=lifespan)
    app.add_middleware(LoggingMiddleware)
    app.include_router(health_router)
    from shared.metrics.router import router as metrics_router

    app.include_router(metrics_router)
    from app.api.proxy import router as proxy_router

    app.include_router(proxy_router)
    from app.api.checkout import router as checkout_router

    app.include_router(checkout_router)
    return app


app = create_app()
