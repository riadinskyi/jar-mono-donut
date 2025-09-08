from pydantic import BaseModel, Field
from typing import Annotated

from api_v1.payment.schemas import DescriptionData
from core.models.order import OrderStatus


class OrderCreate(BaseModel):
    jar_id: DescriptionData.jar_id_description
    comment: Annotated[
        str,
        Field(
            description="З яким описом буде перевірятися наявність транзакції",
            examples=["Місячне заощадження", "Подарунок на день народження від Олежи"],
            max_length=200,
        ),
    ]
    amount: DescriptionData.amount_description


class OrderOut(BaseModel):
    id: int
    jar_id: DescriptionData.jar_id_description
    status: OrderStatus
    amount: int
    comment: str
