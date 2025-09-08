from typing import Optional, Annotated

from pydantic import BaseModel, Field

from core.models.order import OrderStatus


class DescriptionData:
    monobank_transaction_id_description = Annotated[
        str,
        Field(
            description="Токен отриматий від кабінета розробника Монобанк", min_length=5
        ),
    ]

    id_payment_description = Annotated[
        int, Field(description="Внутрішній ідентифікатор транзакції")
    ]
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


class CreatePaymentJarRecord(BaseModel):
    monobank_transaction_id: DescriptionData.monobank_transaction_id_description
    jar_id: DescriptionData.jar_id_description
    amount: int
    description: Optional[str]
    comment: Optional[str]
    time: int


class PaymentSearch(BaseModel):
    jar_id: DescriptionData.jar_id_description
    amount: DescriptionData.amount_description
    comment: str


class PaymentDetailsOut(BaseModel):
    id: DescriptionData.id_payment_description
    jar_id: DescriptionData.jar_id_description
    amount: int
    comment: str
    status: OrderStatus


class PaymentOut(BaseModel):
    id: DescriptionData.id_payment_description
    jar_id: DescriptionData.jar_id_description
    amount: int
    comment: str
    time: int


class TransactionOut(BaseModel):
    transaction_data: PaymentDetailsOut
    signature: str
