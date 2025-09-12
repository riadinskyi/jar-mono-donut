from fastapi import APIRouter, Header
from fastapi.params import Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.payment.dependencies import (
    return_payment_by_id,
    return_payment_by_jar_id_mono,
)
from core import db_helper
from core.utils import encode_jwt

from api_v1.order.crud import search_payment
from api_v1.payment.crud import update_all_jars_payments
from api_v1.payment.schemas import PaymentSearch, PaymentDescriptionData

router = APIRouter(prefix="/payment", tags=["Payment"])


@router.get("/get/by-id")
async def get_payment_by_innie_id(
    payment_id: PaymentDescriptionData.id_payment_description = Query(...),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await return_payment_by_id(transaction_id=payment_id, session=session)


@router.get("/get/by-jar-id-mono")
async def get_payment_mono_id(
    monobank_payment_id: PaymentDescriptionData.monobank_payment_id_query = Query(...),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """Знайти транзакція за унікальний кодом котрий присвоїв Монобанк"""
    return await return_payment_by_jar_id_mono(
        jar_id_mono=monobank_payment_id, session=session
    )


@router.get("/find-payment")
async def find_payment(
    data: PaymentSearch = Query(),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Пошук виконаної транзакції серед уже зареєстрованих у реєстрі. <b>ОНОВЛЮЙТЕ РЕГІСТР ВСІХ ТРАНЗАКЦІЙ ПЕРЕД КОЖНИМ ЗАПИТОМ</b>
    """
    data = await search_payment(
        data=data,
        session=session,
    )

    return {"data": data, "signature": await encode_jwt(data)}


@router.post("/add/payments")
async def add_new_payments(
    monobank_token: str = Header(),
    jar_id: str = Query(),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Оновити реєстр бази даних усіх транзакцій по банці.
    """
    data = await update_all_jars_payments(
        monobank_token=monobank_token, jar_id=jar_id, session=session
    )
    return data
