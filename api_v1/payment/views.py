from typing import Annotated
from fastapi import APIRouter, Header
from fastapi.params import Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.payment.dependencies import return_order_by_id
from core.utils import encode_jwt
from api_v1.payment.crud import (
    search_transaction,
    issue_new_order,
    update_all_jars_payments,
    validate_order,
)

from api_v1.payment.schemas import (
    TransactionSearch,
    OrderCreate,
    OrderOut,
)
from core import db_helper

router = APIRouter(prefix="/order", tags=["Payment"])




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


@router.post("/create")
async def create_order(
    data: Annotated[OrderCreate, Query()],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Створення замовлення для підтвердження винагороди донатеру.
    Ціну вказувати помножену на 100 (12.34 -> 1234)
    """
    return await issue_new_order(data_in=data, session=session)


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


@router.patch("/confirm", response_model=OrderOut)
async def confirm_order(
    order_id: int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Перевірка підтрвердження замовлення

    Підтвердити надання замовлення, якщо не виконані умови для правильної донації.
    Тобто знайти транзакцію та підтвердити її власноруч використовуючи платіжнку інструкцію.
    Для цього потрібно також прикріпити індивідуальний ідентифікатор з виписки банки.
    """
    order_by_id = await return_order_by_id(order_id, session)
    return await validate_order(
        session=session,
        order=order_by_id,
    )
