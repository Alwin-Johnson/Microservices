from fastapi import FastAPI
from app.api.health import router as health_router

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Inventory Service")
    app.include_router(health_router)
    from app.api.inventory import router as inventory_router
    app.include_router(inventory_router)
    return app

app = create_app()
