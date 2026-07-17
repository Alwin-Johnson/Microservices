from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db.dependencies import get_db
from models.schemas import ProcessPaymentRequest, PaymentResponse
from service.payment_service import PaymentService
from shared.errors.exceptions import PlatformError

router = APIRouter(prefix="/payments", tags=["payments"])


def get_payment_service(session: AsyncSession = Depends(get_db)) -> PaymentService:
    return PaymentService(session)


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def process_payment(
    request: ProcessPaymentRequest,
    service: PaymentService = Depends(get_payment_service),
):
    try:
        return await service.process_payment(
            order_id=request.order_id, amount=request.amount
        )
    except PlatformError as e:
        raise e


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID, service: PaymentService = Depends(get_payment_service)
):
    try:
        return await service.get_payment(payment_id)
    except PlatformError as e:
        raise e
