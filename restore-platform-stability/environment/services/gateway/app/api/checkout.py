from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from service.checkout_service import CheckoutService
from shared.errors.exceptions import PlatformError

router = APIRouter(prefix="/checkout", tags=["checkout"])

class CheckoutItem(BaseModel):
    sku: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)

class CheckoutRequest(BaseModel):
    customer_id: str = Field(..., min_length=1)
    items: List[CheckoutItem] = Field(..., min_length=1)

def get_checkout_service() -> CheckoutService:
    return CheckoutService()

@router.post("")
async def execute_checkout(
    request: CheckoutRequest,
    service: CheckoutService = Depends(get_checkout_service)
):
    try:
        items_dict = [{"sku": item.sku, "quantity": item.quantity} for item in request.items]
        return await service.execute_checkout(customer_id=request.customer_id, items=items_dict)
    except PlatformError as e:
        raise e
