from fastapi import HTTPException, status
from api_v1.payment.schemas import PaymentSearch
from api_v1.system.crud import request_jar_info

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
