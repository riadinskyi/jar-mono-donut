from fastapi import APIRouter

from api_v1.system.views import router as system_router

router = APIRouter()
router.include_router(system_router)