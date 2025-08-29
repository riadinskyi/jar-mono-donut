from fastapi import APIRouter, Header
from fastapi.params import Query

from api_v1.payment.crud import search_transaction
from api_v1.payment.schemas import PaymentSearch

router = APIRouter(prefix="/payment",tags=["Payment"])

@router.get("/find-transaction")
async def find_transaction(data:PaymentSearch=Query(),monobank_token: str=Header()):
    """
    Реалізація пошуку транзакцій у клієнта на певній банці.
    """
    return await search_transaction(
        data=data,
        api_token=monobank_token,
    )



