from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

async def check_db_connection(session: AsyncSession) -> bool:
    """Check if the database connection is healthy."""
    from shared.db.session import SessionLocal
    if not SessionLocal:
        return False
    try:
        await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
