from fastapi import APIRouter, Depends, HTTPException, status

from api_v1.auth.helper import authenticate_admin, get_current_admin
from core.utils import encode_jwt, decode_jwt, encode_refresh_jwt
from fastapi import Body

# OAuth2 password flow common endpoint at root level
router = APIRouter(tags=["Auth"])


@router.post("/token")
async def token(admin=Depends(authenticate_admin)):
    payload = {
        "sub": str(admin.id),
        "user_name": str(admin.user_name),
    }
    access_token = await encode_jwt(payload)
    refresh_token = await encode_refresh_jwt(payload)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/me")
async def get_me(admin=Depends(get_current_admin)):
    return {
        "id": admin.id,
        "user_name": admin.user_name,
        "name": admin.name,
    }


@router.post("/refresh")
async def refresh_token_endpoint(refresh_token: str = Body(embed=True)):
    # Validate the refresh token and issue a new access token
    try:
        payload = await decode_jwt(refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    token_type = payload.get("typ")
    sub = payload.get("sub")
    user_name = payload.get("user_name")
    if token_type != "refresh" or (not sub and not user_name):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )

    new_payload = {"sub": sub, "user_name": user_name}
    new_access_token = await encode_jwt(new_payload)
    new_refresh_token = await encode_refresh_jwt(new_payload)
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }
