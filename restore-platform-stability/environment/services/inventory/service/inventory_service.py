from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models.enums import ReservationStatus
from shared.repositories.inventory import InventoryItemRepository, InventoryReservationRepository
from shared.errors.exceptions import NotFoundError, ValidationError

class InventoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.item_repo = InventoryItemRepository(session)
        self.reservation_repo = InventoryReservationRepository(session)

    async def get_item(self, item_id: UUID) -> dict:
        item = await self.item_repo.get(item_id)
        if not item:
            raise NotFoundError("Inventory item not found.")
        return item

    async def reserve_stock(self, order_id: UUID, sku: str, quantity: int) -> dict:
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
            
        item = await self.item_repo.get_by_sku(sku, for_update=True)
        if not item:
            raise NotFoundError(f"Item with SKU {sku} not found.")

        if item.quantity_available < quantity:
            raise ValidationError(f"Insufficient stock for SKU {sku}.")

        # Deduct stock
        item.quantity_available -= quantity
        await self.item_repo.update(item.id, {"quantity_available": item.quantity_available})

        # Create reservation
        reservation = await self.reservation_repo.create({
            "order_id": order_id,
            "item_id": item.id,
            "quantity": quantity,
            "status": ReservationStatus.CONFIRMED
        })

        return reservation

    async def cancel_reservation(self, reservation_id: UUID) -> None:
        reservation = await self.reservation_repo.get(reservation_id)
        if not reservation:
            raise NotFoundError("Reservation not found.")
            
        if reservation.status != ReservationStatus.CONFIRMED:
            raise ValidationError("Only confirmed reservations can be cancelled.")

        item = await self.item_repo.get(reservation.item_id, for_update=True)
        if item:
            item.quantity_available += reservation.quantity
            await self.item_repo.update(item.id, {"quantity_available": item.quantity_available})

        reservation.status = ReservationStatus.CANCELLED
        await self.reservation_repo.update(reservation.id, {"status": reservation.status})
