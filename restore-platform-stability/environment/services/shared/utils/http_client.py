import httpx
from typing import AsyncGenerator

async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """FastAPI dependency for async HTTP client."""
    async with httpx.AsyncClient() as client:
        yield client
