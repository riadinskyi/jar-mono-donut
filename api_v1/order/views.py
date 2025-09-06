from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.order.crud import (
    issue_new_order,
    validate_order,
)
from api_v1.order.dependencies import return_order_by_id
from api_v1.order.schemas import (
    OrderCreate,
    OrderOut,
)
from core import db_helper
from core.utils import encode_jwt

router = APIRouter(prefix="/order", tags=["Order"])


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
    data = await validate_order(
        session=session,
        order=order_by_id,
    )

    return {
        "status_code": 200,
        "comment": "Transaction approved. Order is paid",
        "data": data,
    }
