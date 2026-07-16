from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db.dependencies import get_db
from models.schemas import ReserveStockRequest, InventoryItemResponse, InventoryReservationResponse
from service.inventory_service import InventoryService
from shared.errors.exceptions import PlatformError

router = APIRouter(prefix="/inventory", tags=["inventory"])

def get_inventory_service(session: AsyncSession = Depends(get_db)) -> InventoryService:
    return InventoryService(session)

@router.post("/reserve", response_model=InventoryReservationResponse, status_code=status.HTTP_201_CREATED)
async def reserve_inventory(
    request: ReserveStockRequest,
    service: InventoryService = Depends(get_inventory_service)
):
    try:
        return await service.reserve_stock(order_id=request.order_id, sku=request.sku, quantity=request.quantity)
    except PlatformError as e:
        raise e

@router.post("/release/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def release_inventory(
    reservation_id: UUID,
    service: InventoryService = Depends(get_inventory_service)
):
    try:
        await service.cancel_reservation(reservation_id)
    except PlatformError as e:
        raise e

@router.get("/{sku}", response_model=InventoryItemResponse)
async def get_inventory(
    sku: str,
    service: InventoryService = Depends(get_inventory_service)
):
    try:
        # Re-use item repo internally via a quick direct call or we could add `get_item_by_sku` to the service.
        item = await service.item_repo.get_by_sku(sku)
        if not item:
            from shared.errors.exceptions import NotFoundError
            raise NotFoundError(f"SKU {sku} not found")
        return item
    except PlatformError as e:
        raise e
