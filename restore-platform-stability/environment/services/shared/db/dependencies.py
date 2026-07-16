from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from shared.db.session import SessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions."""
    if not SessionLocal:
        raise ValueError("DATABASE_URL is not configured in this environment.")
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
