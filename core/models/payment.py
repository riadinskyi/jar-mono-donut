from core.base import Base
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class Payment(Base):
    jar_id: Mapped[str] = mapped_column(String(100), nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=True)
    monobank_transaction_id: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    comment: Mapped[str] = mapped_column(String, nullable=True)
    time: Mapped[int] = mapped_column(String, nullable=True)
