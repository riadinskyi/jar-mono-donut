from fastapi import APIRouter

from api_v1.system.views import account_router
from api_v1.system.views import permission_router
from api_v1.system.views import admin_router


from api_v1.order.views import router as order_router
from api_v1.payment.views import router as payment_router
from api_v1.auth.view import router as auth_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(account_router)
router.include_router(admin_router)
router.include_router(permission_router)
router.include_router(order_router)
router.include_router(payment_router)
