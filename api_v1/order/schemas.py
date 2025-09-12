from pydantic import BaseModel, Field
from typing import Annotated

from api_v1.payment.schemas import PaymentDescriptionData
from core.models.order import OrderStatus


class OrderDescriptionData:
    comment: Annotated[
        str,
        Field(
            description="З яким описом буде перевірятися наявність транзакції",
            examples=["Місячне заощадження", "Подарунок на день народження від Олежи"],
            max_length=200,
        ),
    ]


class OrderBase(BaseModel):
    jar_id: PaymentDescriptionData.jar_id_description
    comment: Annotated[
        str,
        Field(
            description="З яким описом буде перевірятися наявність транзакції",
            examples=["Місячне заощадження", "Подарунок на день народження від Олежи"],
            max_length=200,
        ),
    ]

    amount: PaymentDescriptionData.amount_description


class OrderCreate(OrderBase):
    pass


class OrderOut(OrderBase):
    id: int
    status: OrderStatus
