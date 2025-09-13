import uuid
from datetime import timedelta, datetime, timezone

import bcrypt
import jwt
from core.config import settings


async def hash_password(password: bytes):
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password, salt)
    return password


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


async def decode_jwt(
    token: str,
    public_key: str = settings.jwt.public_jwt_path.read_text(),
    algorithms: list[str] | None = None,
) -> dict:
    if algorithms is None:
        algorithms = [settings.jwt.algorithm]
    payload = jwt.decode(token, public_key, algorithms=algorithms)
    return payload
