from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth import auth_by_operation_token
from api_v1.order.crud import (
    issue_new_order,
    validate_order,
    delete_order,
)
from api_v1.order.dependencies import return_order_by_id
from api_v1.order.schemas import (
    OrderCreate,
    OrderOut,
)
from core import db_helper

router = APIRouter(
    prefix="/order", tags=["Order"], dependencies=[Depends(auth_by_operation_token)]
)


@router.get("/get/by-id", response_model=OrderOut)
async def get_order_by_id(
    order_id: int, session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    return await return_order_by_id(order_id=order_id, session=session)


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
    Перевірка підтвердження замовлення
    """
    order_by_id = await return_order_by_id(order_id, session)

    await validate_order(session=session, order=order_by_id)

    return OrderOut(
        id=order_by_id.id,
        jar_id=order_by_id.jar_id,
        status=order_by_id.status,
        amount=order_by_id.amount,
        comment="Transaction approved. Order is paid",
    )


@router.delete("/delete")
async def order_delete(
    order_id: int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Видалення замовлення за номером замовлення
    """
    order_id = await return_order_by_id(order_id=order_id, session=session)
    return await delete_order(
        order=order_id,
        session=session,
    )
