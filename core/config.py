from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

BASE_DIR = Path(__file__).parent.parent

DB_PATH = BASE_DIR / "db.sqlite3"

load_dotenv()
system_token = os.getenv(
    "SYSTEM_TOKEN"
)  # token for creation admin from the name of a system
service_token = os.getenv("SERVICE_TOKEN")  # token for another API system
operation_token = os.getenv("OPERATION_TOKEN")  # token for simple operation auth


def _normalize_database_url(url: str | None) -> str:
    """
    Normalize DATABASE_URL for SQLAlchemy async with psycopg on platforms like Render:
    - Accepts postgres:// or postgresql:// and converts to postgresql+psycopg://
    - Preserves existing async postgresql+psycopg:// URLs
    - Appends sslmode=require for non-local hosts if not provided
    - Supports a bare hostname in DATABASE_URL combined with USER_NAME/PASSWORD/PORT/DB_NAME
    - Falls back to SQLite when url is empty or insufficient data
    """
    default_sqlite = f"sqlite+aiosqlite:///{DB_PATH}"
    if not url:
        return default_sqlite

    # Leave SQLite URLs untouched
    if url.startswith("sqlite+") or url.startswith("sqlite://"):
        return url

    # If URL has no scheme (e.g. just host), attempt to build from separate env vars
    if "://" not in url:
        host = url.strip()
        if not host:
            return default_sqlite
        # Accept multiple common env var names
        user = os.getenv("USER_NAME") or os.getenv("POSTGRES_USER") or os.getenv("PGUSER")
        password = os.getenv("PASSWORD") or os.getenv("POSTGRES_PASSWORD") or os.getenv("PGPASSWORD")
        port = os.getenv("PORT") or os.getenv("POSTGRES_PORT") or os.getenv("PGPORT") or "5432"
        db_name = (
            os.getenv("DB_NAME")
            or os.getenv("DATABASE_NAME")
            or os.getenv("POSTGRES_DB")
            or os.getenv("PGDATABASE")
            or user
        )
        # If we still don't have the minimum required parts, fallback to sqlite
        if not (user and db_name):
            return default_sqlite
        # Password may be optional for some setups
        auth = f"{user}:{password}@" if password is not None else f"{user}@"
        url = f"postgresql+psycopg://{auth}{host}:{port}/{db_name}"

    # Normalize scheme
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    # If it's still sync driver, upgrade to async psycopg
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]

    # Ensure sslmode=require for non-local hosts if not specified
    try:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        is_local = host in {"localhost", "127.0.0.1"} or host.endswith(".internal")
        query = parse_qs(parsed.query, keep_blank_values=True)
        if not is_local and "sslmode" not in {k.lower() for k in query.keys()}:
            # add sslmode=require
            query["sslmode"] = ["require"]
            new_query = urlencode({k: v[0] for k, v in query.items()})
            url = urlunparse(
                (
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    new_query,
                    parsed.fragment,
                )
            )
    except Exception:
        # If anything goes wrong, just return the best-effort url
        return url

    return url


class DbSettings(BaseModel):
    url: str = _normalize_database_url(os.getenv("DATABASE_URL"))
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
