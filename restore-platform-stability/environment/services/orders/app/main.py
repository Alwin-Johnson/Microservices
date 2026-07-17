from fastapi import FastAPI
from contextlib import asynccontextmanager
from shared.logger.custom_logger import setup_logger
from shared.middleware.logging import LoggingMiddleware
from app.api.health import router as health_router

logger = setup_logger("orders")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Service starting up...")
    yield
    logger.info("Service shutting down...")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Orders Service", lifespan=lifespan)
    app.add_middleware(LoggingMiddleware)
    app.include_router(health_router)
    from shared.metrics.router import router as metrics_router
    app.include_router(metrics_router)
    from app.api.orders import router as orders_router
    app.include_router(orders_router)
    return app

app = create_app()
