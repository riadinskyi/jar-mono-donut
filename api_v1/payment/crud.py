from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.order import Order
from api_v1.payment.schemas import PaymentSearch, CreatePayment
from api_v1.system.crud import request_jar_info


async def issue_new_transaction(data_in:CreatePayment, session:AsyncSession):
    new_transaction=Order(
        jar_id=data_in.jar_id,
        amount=data_in.amount,
        description=data_in.description,
        timestamp=datetime.now().timestamp()
    )
    session.add(new_transaction)
    await session.commit()
    await session.refresh(new_transaction)
    return new_transaction


async def search_transaction(data: PaymentSearch, api_token: str):
    try:
        request = await request_jar_info(jar_id=data.jar_id, api_token=api_token)

        found_transactions = []
        for transaction in request:
            amount_match = transaction.get("amount") == data.amount
            comment_match = transaction.get("comment") == data.description

            if amount_match and comment_match:
                found_transactions.append(transaction)

        if not found_transactions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No transactions found with amount {data.amount} and description '{data.description}'"
            )

        return found_transactions

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching transactions: {str(e)}"
        )
