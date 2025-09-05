from fastapi import HTTPException, status

from api_v1.system.crud import request_jar_info
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.order import Order, OrderStatus
from core.models.payment import Payment
from api_v1.payment.schemas import CreatePaymentJarRecord, OrderOut


async def return_order_by_id(order_id: int, session: AsyncSession) -> OrderOut:
    stmt = select(Order).where(Order.id == order_id)
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()
    return order


async def return_transaction_by_id(transaction_id: int, session: AsyncSession):
    stmt = select(Payment).where(Payment.id == transaction_id)
    result = await session.execute(stmt)
    transaction = result.scalar_one_or_none()
    return transaction


async def return_transaction_by_jar_id_mono(jar_id_mono: str, session: AsyncSession):
    stmt = select(Payment).where(Payment.monobank_transaction_id == jar_id_mono)
    result = await session.execute(stmt)
    transaction = result.scalar_one_or_none()
    return transaction is not None


async def connect_order_to_transaction(
    order: Order, transaction: Payment, session: AsyncSession
):

    if transaction.order_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot use this transaction. Reach admin help",
        )
    # connect order to transaction record
    transaction.order_id = order.id
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)

    # update order data
    order.payment_id = transaction
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


async def change_order_status(
    order: Order, session: AsyncSession, status_to_set: OrderStatus
):
    order.status = status_to_set
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


async def add_payment_if_not_exists(
    data_in: CreatePaymentJarRecord, session: AsyncSession
):
    """
    Додає нову транзакцію, тільки якщо такої з monobank_transaction_id ще нема.
    Повертає новий запис, або None якщо транзакція вже існує.
    """
    stmt = select(Payment).where(
        Payment.monobank_transaction_id == data_in.monobank_transaction_id
    )
    result = await session.execute(stmt)
    existing_transaction = result.scalar_one_or_none()

    if existing_transaction:
        # Транзакція вже існує – нічого не робимо
        return None

    new_transaction = Payment(
        jar_id=data_in.jar_id,
        monobank_transaction_id=data_in.monobank_transaction_id,
        amount=data_in.amount,
        description=data_in.description,
        comment=data_in.comment,
        time=data_in.time,
    )
    session.add(new_transaction)
    await session.commit()
    await session.refresh(new_transaction)
    return new_transaction


async def return_all_transaction(jar_id: str, monobank_token: str):
    request = await request_jar_info(jar_id=jar_id, api_token=monobank_token)
    return request
