from pydantic import BaseModel, Field
from typing import Annotated
from core.models.order import OrderStatus


jar_id_description = Annotated[
    str,
    Field(
        description="Унікальний ідентифікатор отриманий від монобанку про рахунки з акаунту користувача",
        examples=["fnrgruejdbvhkf", "fhreyfgerf"],
        min_length=1,
    ),
]
amount_description = Annotated[
    int,
    Field(
        description="Ціле число помножене на сто (12.34 грн -> 1234)",
        examples=[1000, 5000],
        gt=0,
    ),
]


class OrderCreate(BaseModel):
    jar_id: jar_id_description
    comment: Annotated[
        str,
        Field(
            description="З яким описом буде перевірятися наявність транзакції",
            examples=["Місячне заощадження", "Подарунок на день народження від Олежи"],
            max_length=200,
        ),
    ]
    amount: amount_description


class OrderOut(BaseModel):
    id: int
    jar_id: jar_id_description
    status: OrderStatus
    amount: int
    comment: str
