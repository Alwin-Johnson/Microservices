import redis.asyncio as redis
from shared.config.settings import settings
from typing import AsyncGenerator
from shared.metrics.prometheus import REDIS_CONNECTIONS_IN_USE

# Use a global connection pool
redis_client = None
if settings.redis_url:
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    # Set the gauge to read from the pool size dynamically
    REDIS_CONNECTIONS_IN_USE.set_function(
        lambda: len(redis_client.connection_pool._in_use_connections)
        if redis_client
        else 0
    )


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """FastAPI dependency for Redis async client."""
    if not redis_client:
        raise ValueError("REDIS_URL is not configured in this environment.")
    try:
        yield redis_client
    finally:
        # We don't close the global client here.
        pass
