from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models.enums import OrderStatus
from shared.repositories.orders import OrderRepository
from shared.errors.exceptions import NotFoundError, ValidationError


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_repo = OrderRepository(session)

    async def create_order(self, customer_id: str, total_amount: Decimal) -> dict:
        if not customer_id:
            raise ValidationError("Customer ID is required.")
        if total_amount <= 0:
            raise ValidationError("Total amount must be greater than zero.")

        # Create the order in PENDING status
        order = await self.order_repo.create(
            {
                "customer_id": customer_id,
                "total_amount": total_amount,
                "status": OrderStatus.PENDING,
            }
        )

        return order

    async def complete_order(self, order_id: UUID) -> dict:
        order = await self.order_repo.get(order_id)
        if not order:
            raise NotFoundError("Order not found.")

        if order.status != OrderStatus.PENDING:
            raise ValidationError(f"Cannot complete order in {order.status} status.")

        order.status = OrderStatus.COMPLETED
        await self.order_repo.update(order.id, {"status": order.status})

        return order

    async def fail_order(self, order_id: UUID) -> dict:
        order = await self.order_repo.get(order_id)
        if not order:
            raise NotFoundError("Order not found.")

        order.status = OrderStatus.FAILED
        await self.order_repo.update(order.id, {"status": order.status})

        return order

    async def get_order(self, order_id: UUID) -> dict:
        order = await self.order_repo.get(order_id)
        if not order:
            raise NotFoundError("Order not found.")
        return order

    async def get_orders_by_customer(self, customer_id: str) -> list:
        return await self.order_repo.get_by_customer_id(customer_id)
