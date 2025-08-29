from fastapi import APIRouter

from api_v1.system.views import router as system_router
from api_v1.payment.views import router as payment_router

router = APIRouter()
router.include_router(system_router)
router.include_router(payment_router)