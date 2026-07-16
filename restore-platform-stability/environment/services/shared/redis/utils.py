import redis.asyncio as redis
import logging
from shared.config.settings import settings

logger = logging.getLogger(__name__)

async def check_redis_connection() -> bool:
    """Check if the Redis connection is healthy."""
    if not settings.redis_url:
        return False
    try:
        client = redis.from_url(settings.redis_url, decode_responses=True)
        await client.ping()
        await client.aclose()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False
