from typing import Sequence, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models.order import Order
from shared.repositories.base import BaseRepository

class OrderRepository(BaseRepository[Order]):
    def __init__(self, session: AsyncSession):
        super().__init__(Order, session)

    async def get_by_customer_id(self, customer_id: str) -> Sequence[Order]:
        """Fetch all orders for a given customer."""
        result = await self.session.execute(
            select(self.model).where(self.model.customer_id == customer_id)
        )
        return result.scalars().all()
