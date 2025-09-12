from typing import Optional, Annotated

from pydantic import BaseModel, Field

from core.models.order import OrderStatus


class PaymentDescriptionData:
    monobank_transaction_id_description = Annotated[
        str,
        Field(
            title="monobank_transaction_id",
            description="Токен отриматий від кабінета розробника Монобанк",
            min_length=5,
        ),
    ]

    monobank_payment_id_query = Annotated[
        str,
        Field(
            description="Унікальний ідентифікатор транзакції, присвоєний Монобанком",
            examples=["qweasd123", "trn_9876543210"],
            min_length=3,
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
    comment_description = Annotated[
        str,
        Field(
            description="Коментар за яким буде проведена перевірка на наявність в реєстрі такої транзакції"
        ),
    ]


class PaymentBase(BaseModel):
    jar_id: PaymentDescriptionData.jar_id_description
    amount: PaymentDescriptionData.amount_description
    comment: PaymentDescriptionData.comment_description


class PaymentSearch(PaymentBase):
    pass


class SearchPaymentInnieID(BaseModel):
    id_payment: PaymentDescriptionData.id_payment_description


class CreatePaymentJarRecord(PaymentBase):
    comment: Optional[str] = None
    monobank_transaction_id: str = Field(alias="id")
    description: Optional[str] = None
    time: int


class PaymentDetailsOut(PaymentBase):
    id: PaymentDescriptionData.id_payment_description
    status: OrderStatus


class PaymentOut(BaseModel):
    id: PaymentDescriptionData.id_payment_description
    jar_id: PaymentDescriptionData.jar_id_description
    amount: PaymentDescriptionData.amount_description
    comment: Optional[str] = None
    time: float


class SignedPaymentOut(BaseModel):
    payment_data: PaymentDetailsOut
    signature: str
