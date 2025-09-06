from typing import Optional

from pydantic import BaseModel

from api_v1.order.schemas import amount_description
from core.models.order import OrderStatus


class CreatePaymentJarRecord(BaseModel):
    jar_id: str
    monobank_transaction_id: str
    amount: int
    description: Optional[str]
    comment: Optional[str]
    time: int


class TransactionSearch(BaseModel):
    jar_id: str
    amount: amount_description
    comment: str


class TransactionDetailsOut(BaseModel):
    id: int
    jar_id: str
    amount: int
    comment: str
    status: OrderStatus


class PaymentDetailsOut(BaseModel):
    id: int
    jar_id: str
    amount: int
    comment: str
    time: int


class TransactionOut(BaseModel):
    transaction_data: TransactionDetailsOut
    signature: str
