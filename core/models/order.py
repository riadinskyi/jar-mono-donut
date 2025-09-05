from enum import Enum

from sqlalchemy import String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from core.base import Base


class OrderStatus(str, Enum):
    created = "created"
    paid = "paid"
    canceled_by_system = "canceled"
    canceled_by_client = "canceled_by_client"
    canceled_by_data_update = "canceled_by_data_update"
    canceled_by_admin = "canceled_by_admin"


class Order(Base):
    jar_id: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False)
    timestamp: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus, name="order_status", create_constraint=True),
        nullable=False,
        default=OrderStatus.created,
    )

    comment: Mapped[str] = mapped_column(String(100), nullable=False)
