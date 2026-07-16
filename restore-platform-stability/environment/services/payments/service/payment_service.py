from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models.enums import PaymentStatus
from shared.repositories.payments import PaymentRepository
from shared.errors.exceptions import NotFoundError, ValidationError

class PaymentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.payment_repo = PaymentRepository(session)

    async def process_payment(self, order_id: UUID, amount: Decimal) -> dict:
        if amount <= 0:
            raise ValidationError("Payment amount must be greater than zero.")

        # In a real system, we'd integrate with a payment gateway (Stripe, etc.) here.
        # For this mock, we assume successful payment processing.
        
        payment = await self.payment_repo.create({
            "order_id": order_id,
            "amount": amount,
            "status": PaymentStatus.SUCCESS
        })
        
        return payment

    async def get_payment(self, payment_id: UUID) -> dict:
        payment = await self.payment_repo.get(payment_id)
        if not payment:
            raise NotFoundError("Payment not found.")
        return payment

    async def get_payments_for_order(self, order_id: UUID) -> list:
        return await self.payment_repo.get_by_order_id(order_id)
