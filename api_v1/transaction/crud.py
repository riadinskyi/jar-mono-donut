from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.payment import Payment

from api_v1.transaction.schemas import (
    TransactionSearch,
    CreatePaymentJarRecord,
    PaymentDetailsOut,
)
from api_v1.transaction.dependencies import (
    add_payment_if_not_exists,
)
from api_v1.system.crud import request_jar_info


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
        return dict(
            status_code=status.HTTP_201_CREATED,
            detail={"message": "New payments added", "data": new_payments},
        )
    return "Everything is up to date"
