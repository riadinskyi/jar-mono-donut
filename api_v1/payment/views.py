from fastapi import APIRouter, Header
from fastapi.params import Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.payment.crud import search_transaction, issue_new_transaction
from api_v1.payment.schemas import PaymentSearch, CreatePayment
from core import db_helper

router = APIRouter(prefix="/order",tags=["Payment"])

@router.get("/find-transaction")
async def find_transaction(data:PaymentSearch=Query(),monobank_token: str=Header()):
    """
    Реалізація пошуку транзакцій у клієнта на певній банці.
    """
    return await search_transaction(
        data=data,
        api_token=monobank_token,
    )

@router.post("/create")
async def create_order(
        data:CreatePayment,
        session:AsyncSession=Depends(db_helper.scoped_session_dependency)
):
    """
    Створення замовлення, щоб отримати підтрведження про винагороду донатеру. Ціну вказувати помножену на 100 (12.34 -> 1234)
    """
    return await issue_new_transaction(data_in=data, session=session)

