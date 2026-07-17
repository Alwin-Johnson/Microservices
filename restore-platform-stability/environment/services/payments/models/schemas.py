from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ProcessPaymentRequest(BaseModel):
    order_id: UUID
    amount: float = Field(..., gt=0)


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    amount: float
    status: str
    created_at: datetime
    updated_at: datetime
