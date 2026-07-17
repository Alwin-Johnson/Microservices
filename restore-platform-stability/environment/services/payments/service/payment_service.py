from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models.enums import PaymentStatus
from shared.repositories.payments import PaymentRepository
from shared.errors.exceptions import NotFoundError, ValidationError
import asyncio
from shared.redis.client import redis_client

LOAD_SHEDDING_SEMAPHORE = asyncio.Semaphore(5)

class PaymentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.payment_repo = PaymentRepository(session)

    async def process_payment(self, order_id: UUID, amount: Decimal) -> dict:
        import time
        from shared.metrics.prometheus import PAYMENT_LATENCY
        start_time = time.perf_counter()
        
        if amount <= 0:
            raise ValidationError("Payment amount must be greater than zero.")

        import time
        from shared.config.settings import settings
        
        # Apply load shedding backpressure if active
        if settings.fault_mode == "on" and redis_client:
            is_active = await redis_client.get("fault_active")
            if is_active:
                async with LOAD_SHEDDING_SEMAPHORE:
                    await asyncio.sleep(0.5)

        payment = await self.payment_repo.create({
            "order_id": order_id,
            "amount": amount,
            "status": PaymentStatus.SUCCESS
        })
        
        PAYMENT_LATENCY.observe(time.perf_counter() - start_time)
        return payment

    async def get_payment(self, payment_id: UUID) -> dict:
        payment = await self.payment_repo.get(payment_id)
        if not payment:
            raise NotFoundError("Payment not found.")
        return payment

    async def get_payments_for_order(self, order_id: UUID) -> list:
        return await self.payment_repo.get_by_order_id(order_id)
