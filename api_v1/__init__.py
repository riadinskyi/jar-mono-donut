from fastapi import APIRouter

from api_v1.system.views import router as system_router
from api_v1.order.views import router as order_router
from api_v1.transaction.views import router as transaction_router

router = APIRouter()
router.include_router(system_router)
router.include_router(order_router)
router.include_router(transaction_router)
