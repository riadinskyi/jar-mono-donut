from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.payment import Payment
from core.models.order import Order, OrderStatus

from api_v1.payment.schemas import (
    TransactionSearch,
    OrderCreate,
    CreatePaymentJarRecord,
    PaymentDetailsOut,
)
from api_v1.payment.dependencies import (
    add_payment_if_not_exists,
    change_order_status,
    connect_order_to_transaction,
    return_transaction_by_id,
)
from api_v1.system.crud import request_jar_info


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
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="Transaction approved. Order is paid",
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


async def search_transaction(data: TransactionSearch, session: AsyncSession) -> dict:
    """
    Пошук виконаної транзакції серед уже зареєстрованих у реєстрі.
    :param data: Дані, за якими виконується пошук в базі даних
    :param session: сесія бази даних
    :return: знайдена транзація в регістрі
    """
    stmt = select(Payment).where(
        Payment.jar_id == data.jar_id,
        Payment.amount == data.amount,
        Payment.comment == data.comment,
    )
    result = await session.execute(stmt)
    payment = result.scalars().first()
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    payment_data = PaymentDetailsOut(
        id=payment.id,
        jar_id=payment.jar_id,
        amount=payment.amount,
        comment=payment.comment,
        time=payment.time,
    )
    return dict(payment_data)


async def update_all_jars_payments(
    monobank_token: str, jar_id: str, session: AsyncSession
):
    transactions = await request_jar_info(jar_id=jar_id, api_token=monobank_token)
    new_payments = []

    for transaction in transactions:
        record = CreatePaymentJarRecord(
            jar_id=jar_id,
            monobank_transaction_id=transaction["id"],
            amount=transaction["amount"],
            description=transaction.get("description"),
            comment=transaction.get("comment"),
            time=transaction["time"],
        )
        new_transaction = await add_payment_if_not_exists(record, session)
        if new_transaction:
            new_payments.append(new_transaction)
    if new_payments:  # Якщо список НЕ пустий -> повернути створені
        raise HTTPException(
            status_code=status.HTTP_201_CREATED,
            detail={"message": "New payments added", "data": new_payments},
        )
    return "Everything is up to date"
