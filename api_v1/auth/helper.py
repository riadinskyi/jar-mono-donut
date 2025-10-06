import bcrypt
from fastapi import Form, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Form, HTTPException, status, Depends, Security
from fastapi.security import (
    OAuth2PasswordBearer,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from core import Admin, db_helper
from core.utils import decode_jwt


security = OAuth2PasswordBearer(tokenUrl="token")


async def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


async def authenticate_admin(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    user_name: str = Form(None),
    username: str | None = Form(None),
    password: str = Form(...),
) -> Admin:
    effective_user_name = user_name or username
    if not effective_user_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="'user_name' or 'username' is required",
        )
    result = await session.execute(
        select(Admin).where(Admin.user_name == effective_user_name)
    )
    admin = result.scalars().first()
    if not admin or not await validate_password(
        password,
        admin.password.encode() if isinstance(admin.password, str) else admin.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return admin


async def get_current_admin(
    token: str = Depends(security),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> Admin:
    try:
        payload = await decode_jwt(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    admin_id = payload.get("sub")
    user_name = payload.get("user_name")
    if not admin_id and not user_name:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    query = select(Admin)
    if admin_id:
        query = query.where(Admin.id == int(admin_id))
    elif user_name:
        query = query.where(Admin.user_name == user_name)

    result = await session.execute(query)
    admin = result.scalars().first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return admin
