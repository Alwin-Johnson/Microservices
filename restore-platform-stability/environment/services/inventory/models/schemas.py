from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ReserveStockRequest(BaseModel):
    order_id: UUID
    sku: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)


class InventoryItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sku: str
    quantity_available: int
    price: float
    created_at: datetime
    updated_at: datetime


class InventoryReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    item_id: UUID
    quantity: int
    status: str
    created_at: datetime
    updated_at: datetime
