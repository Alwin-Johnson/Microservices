import redis.asyncio as redis
from shared.config.settings import settings
from typing import AsyncGenerator

async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """FastAPI dependency for Redis async client."""
    if not settings.redis_url:
        raise ValueError("REDIS_URL is not configured in this environment.")
    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()
