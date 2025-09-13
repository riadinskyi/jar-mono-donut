from fastapi import APIRouter, Depends

from api_v1.auth.helper import authenticate_admin
from core.utils import encode_jwt

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
async def login(admin=Depends(authenticate_admin)):
    payload = {
        "sub": str(admin.id),
        "user_name": str(admin.user_name),
    }
    token = await encode_jwt(payload)
    return {"access_token": token, "token_type": "bearer"}
