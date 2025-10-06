from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent

DB_PATH = BASE_DIR / "db.sqlite3"

load_dotenv()
system_token = os.getenv(
    "SYSTEM_TOKEN"
)  # token for creation admin from the name of a system
service_token = os.getenv("SERVICE_TOKEN")  # token for another API system
operation_token = os.getenv("OPERATION_TOKEN")  # token for simple operation auth


class DbSettings(BaseModel):
    url: str = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DB_PATH}")
    echo: bool = False


class AuthJWT(BaseModel):
    private_jwt_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_jwt_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 14


class Settings(BaseSettings):
    api_v1_prefix: str = "/api/v1"
    jwt: AuthJWT = AuthJWT()
    db: DbSettings = DbSettings()


settings = Settings()
