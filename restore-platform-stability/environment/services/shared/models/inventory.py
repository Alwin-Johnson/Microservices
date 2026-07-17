import uuid
from decimal import Decimal
from sqlalchemy import (
    String,
    Integer,
    Numeric,
    Enum as SQLEnum,
    ForeignKey,
    text,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.db.base import Base, TimestampMixin
from shared.models.enums import ReservationStatus


class InventoryItem(Base, TimestampMixin):
    __tablename__ = "inventory_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    sku: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    quantity_available: Mapped[int] = mapped_column(Integer, default=0)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    __table_args__ = (
        CheckConstraint("quantity_available >= 0", name="check_quantity_positive"),
    )

    # Relationships
    reservations = relationship("InventoryReservation", back_populates="item")


class InventoryReservation(Base, TimestampMixin):
    __tablename__ = "inventory_reservations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_items.id"), index=True
    )
    quantity: Mapped[int] = mapped_column(Integer)
    status: Mapped[ReservationStatus] = mapped_column(
        SQLEnum(ReservationStatus, name="reservation_status_enum", create_type=False),
        default=ReservationStatus.PENDING,
        index=True,
    )

    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_reservation_quantity_positive"),
    )

    # Relationships
    item = relationship("InventoryItem", back_populates="reservations")
