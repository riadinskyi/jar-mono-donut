from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import service_token
from core.models.order import Order, OrderStatus
from core.models.payment import Payment


async def check_service_token(token: str) -> bool:
    if token != service_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return True


async def return_order_by_id(order_id: int, session: AsyncSession) -> Order:
    stmt = select(Order).where(Order.id == order_id)
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return order


async def change_order_status(
    order: Order, session: AsyncSession, status_to_set: OrderStatus
):
    order.status = status_to_set
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


async def connect_order_to_payment(
    order: Order, transaction: Payment, session: AsyncSession
):

    if transaction.order_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot use this payment. Reach admin help",
        )
    # connect payment to order record
    transaction.order_id = order.id
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)

    # update payment data
    order.payment_id = transaction
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order
