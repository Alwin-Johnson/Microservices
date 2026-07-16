from typing import Sequence, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models.inventory import InventoryItem, InventoryReservation
from shared.repositories.base import BaseRepository

class InventoryItemRepository(BaseRepository[InventoryItem]):
    def __init__(self, session: AsyncSession):
        super().__init__(InventoryItem, session)

    async def get_by_sku(self, sku: str, for_update: bool = False) -> Optional[InventoryItem]:
        """Fetch an inventory item by its SKU."""
        stmt = select(self.model).where(self.model.sku == sku)
        if for_update:
            stmt = stmt.with_for_update()
        result = await self.session.execute(stmt)
        return result.scalars().first()

class InventoryReservationRepository(BaseRepository[InventoryReservation]):
    def __init__(self, session: AsyncSession):
        super().__init__(InventoryReservation, session)

    async def get_by_order_id(self, order_id: UUID | str) -> Sequence[InventoryReservation]:
        """Fetch all reservations associated with a specific order."""
        result = await self.session.execute(
            select(self.model).where(self.model.order_id == order_id)
        )
        return result.scalars().all()
