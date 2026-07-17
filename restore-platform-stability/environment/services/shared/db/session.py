from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from shared.config.settings import settings
from shared.metrics.prometheus import DB_CONNECTIONS_IN_USE

engine = (
    create_async_engine(
        settings.database_url,
        pool_size=40,
        max_overflow=10,
        pool_reset_on_return=None,
        echo=False,
    )
    if settings.database_url
    else None
)
SessionLocal = (
    async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    if engine
    else None
)

if engine:

    @event.listens_for(engine.sync_engine.pool, "checkout")
    def receive_checkout(dbapi_connection, connection_record, connection_proxy):
        DB_CONNECTIONS_IN_USE.inc()

    @event.listens_for(engine.sync_engine.pool, "checkin")
    def receive_checkin(dbapi_connection, connection_record):
        DB_CONNECTIONS_IN_USE.dec()
