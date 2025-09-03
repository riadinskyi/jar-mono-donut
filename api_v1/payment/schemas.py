from pydantic import BaseModel, Field
from typing import Annotated

class PaymentSearch(BaseModel):
    jar_id:str
    amount:int
    description:str



class CreatePayment(BaseModel):
    jar_id: Annotated[str, Field(
        description="Унікальний ідентифікатор отриманий від монобанку про рахунки з акаунту користувача",
        examples=["fnrgruejdbvhkf", "fhreyfgerf"],
        min_length=1,
    )]
    description: Annotated[str, Field(
        description="З яким описом буде перевірятися наявність транзакції",
        examples=["Місячне заощадження", "Подарунок на день народження від Олежи"],
        max_length=200
    )]
    amount: Annotated[int, Field(
        description="Ціле число помножене на сто (12.34 грн -> 1234)",
        examples=[1000, 5000],
        gt=0
    )]