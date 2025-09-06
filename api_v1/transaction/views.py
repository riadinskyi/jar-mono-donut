from fastapi import APIRouter, Header
from fastapi.params import Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_helper
from core.utils import encode_jwt

from api_v1.order.crud import search_transaction
from api_v1.transaction.crud import update_all_jars_payments
from api_v1.transaction.schemas import TransactionSearch


router = APIRouter(prefix="/transaction", tags=["Transaction"])


@router.get("/find-transaction")
async def find_transaction(
    data: TransactionSearch = Query(),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Пошук виконаної транзакції серед уже зареєстрованих у реєстрі. <b>ОНОВЛЮЙТЕ РЕГІСТР ВСІХ ТРАНЗАКЦІЙ ПЕРЕД КОЖНИМ ЗАПИТОМ</b>
    """
    data = await search_transaction(
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
