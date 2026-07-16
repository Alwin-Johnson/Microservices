from fastapi import FastAPI
from app.api.health import router as health_router

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Payments Service")
    app.include_router(health_router)
    from app.api.payments import router as payments_router
    app.include_router(payments_router)
    return app

app = create_app()
