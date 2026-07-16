from typing import List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class OrderItem(BaseModel):
    sku: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)

class CreateOrderRequest(BaseModel):
    customer_id: str = Field(..., min_length=1)
    total_amount: float = Field(..., gt=0)

class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    customer_id: str
    total_amount: float
    status: str
    created_at: datetime
    updated_at: datetime
