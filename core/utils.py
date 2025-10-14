import uuid
from datetime import timedelta, datetime, timezone

import bcrypt
import jwt
from fastapi import HTTPException, status

from core.config import settings, system_token


async def check_system_token_to_auth(token: str):
    """Перевіряти токен на валідність, щоб створити адміністратора від імені системи"""
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    if token != system_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token is not valid"
        )
    return True


async def hash_password(password: bytes) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    # store as text, not bytes, to fit VARCHAR columns and avoid psycopg byte adaptation issues
    # зберігати як текст, а не як байти, щоб уникнути проблеми з postgresql
    return hashed.decode("utf-8")


async def encode_jwt(
    payload: dict,
    private_key: str = settings.jwt.private_jwt_path.read_text(),
    algorithm: str = settings.jwt.algorithm,
    expire_minutes: int = settings.jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)

    to_encode.update(
        exp=expire,
        iat=now,
        jti=str(uuid.uuid4()),
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded


async def encode_refresh_jwt(
    payload: dict,
    expire_minutes: int = settings.jwt.refresh_token_expire_minutes,
) -> str:

    payload_with_type = payload.copy()
    payload_with_type.update({"typ": "refresh"})
    return await encode_jwt(payload_with_type, expire_minutes=expire_minutes)


async def decode_jwt(
    token: str,
    public_key: str = settings.jwt.public_jwt_path.read_text(),
    algorithms: list[str] | None = None,
) -> dict:
    if algorithms is None:
        algorithms = [settings.jwt.algorithm]
    payload = jwt.decode(token, public_key, algorithms=algorithms)
    return payload
