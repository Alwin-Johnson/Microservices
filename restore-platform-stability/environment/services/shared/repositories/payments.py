from typing import Sequence, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models.payment import Payment
from shared.repositories.base import BaseRepository

class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Payment, session)

    async def get_by_order_id(self, order_id: UUID | str) -> Sequence[Payment]:
        """Fetch all payments associated with an order."""
        result = await self.session.execute(
            select(self.model).where(self.model.order_id == order_id)
        )
        return result.scalars().all()
