from pydantic import BaseModel


class PaymentSearch(BaseModel):
    jar_id:str
    amount:int
    description:str

