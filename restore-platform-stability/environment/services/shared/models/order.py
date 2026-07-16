import uuid
from decimal import Decimal
from sqlalchemy import String, Numeric, Enum as SQLEnum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.db.base import Base, TimestampMixin
from shared.models.enums import OrderStatus

class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()")
    )
    customer_id: Mapped[str] = mapped_column(String(255), index=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus, name="order_status_enum", create_type=False),
        default=OrderStatus.PENDING,
        index=True
    )

    # Relationships
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
