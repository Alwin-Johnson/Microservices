from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db.dependencies import get_db
from models.schemas import CreateOrderRequest, OrderResponse
from service.order_service import OrderService
from shared.errors.exceptions import PlatformError

router = APIRouter(prefix="/orders", tags=["orders"])


def get_order_service(session: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(session)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: CreateOrderRequest, service: OrderService = Depends(get_order_service)
):
    try:
        return await service.create_order(
            customer_id=request.customer_id, total_amount=request.total_amount
        )
    except PlatformError as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: UUID, service: OrderService = Depends(get_order_service)):
    try:
        return await service.get_order(order_id)
    except PlatformError as e:
        raise e


@router.get("/customer/{customer_id}", response_model=List[OrderResponse])
async def list_orders(
    customer_id: str, service: OrderService = Depends(get_order_service)
):
    return await service.get_orders_by_customer(customer_id)


@router.patch("/{order_id}/complete", response_model=OrderResponse)
async def complete_order(
    order_id: UUID, service: OrderService = Depends(get_order_service)
):
    try:
        return await service.complete_order(order_id)
    except PlatformError as e:
        raise e


@router.patch("/{order_id}/fail", response_model=OrderResponse)
async def fail_order(
    order_id: UUID, service: OrderService = Depends(get_order_service)
):
    try:
        return await service.fail_order(order_id)
    except PlatformError as e:
        raise e
