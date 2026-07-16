from fastapi import FastAPI
from app.api.health import router as health_router

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Orders Service")
    app.include_router(health_router)
    from app.api.orders import router as orders_router
    app.include_router(orders_router)
    return app

app = create_app()
