from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.order.dependencies import (
    connect_order_to_transaction,
    change_order_status,
)
from api_v1.transaction.crud import search_transaction

from api_v1.order.schemas import (
    OrderCreate,
)
from api_v1.transaction.dependencies import return_transaction_by_id
from api_v1.transaction.schemas import TransactionSearch
from core.models.order import Order, OrderStatus


async def validate_order(
    session: AsyncSession,
    order: Order,
):

    if order.status == OrderStatus.paid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Order is paid"
        )

    validation_approve = await search_transaction(
        data=TransactionSearch(
            jar_id=order.jar_id, amount=order.amount, comment=order.comment
        ),
        session=session,
    )
    transaction_data = await return_transaction_by_id(
        transaction_id=validation_approve["id"], session=session
    )
    if validation_approve:
        if validation_approve["time"] > order.timestamp:
            await change_order_status(
                order=order, status_to_set=OrderStatus.paid, session=session
            )
            await connect_order_to_transaction(order, transaction_data, session)
            return dict(
                data=order,
                status_code=status.HTTP_200_OK,
            )
        else:
            print(validation_approve["time"])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transaction is not valid",
            )


async def issue_new_order(data_in: OrderCreate, session: AsyncSession):
    """
    Створення нового замовлення
    :return: Новостворену транзакцію
    """
    new_transaction = Order(
        jar_id=data_in.jar_id,
        amount=data_in.amount,
        comment=data_in.comment,
        timestamp=datetime.now().timestamp(),
    )
    session.add(new_transaction)
    await session.commit()
    await session.refresh(new_transaction)
    return new_transaction
