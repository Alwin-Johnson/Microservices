import time
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from shared.db.session import SessionLocal
from shared.logger.custom_logger import setup_logger

logger = setup_logger("db_transaction")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions."""
    if not SessionLocal:
        raise ValueError("DATABASE_URL is not configured in this environment.")
    
    start_time = time.perf_counter()
    logger.info("Database transaction started.")
    
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
            duration = time.perf_counter() - start_time
            logger.info("Database transaction committed.", extra={"extra_info": {"duration_s": round(duration, 4)}})
        except BaseException as e:
            await session.rollback()
            duration = time.perf_counter() - start_time
            logger.error("Database transaction failed and rolled back.", extra={"extra_info": {"error": str(e), "duration_s": round(duration, 4)}})
            raise
        finally:
            await session.close()
