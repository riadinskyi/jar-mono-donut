import datetime
import requests

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.admin import Admin


async def request_info_about_client(token: str):
    api = requests.get(
        "https://api.monobank.ua/personal/client-info", headers={"X-Token": token}
    ).json()
    print("MONO API CALL")
    return api


async def check_user_name_availability(user_name: str, session: AsyncSession) -> bool:
    """
    Перевірити, чи існує user_name, якщо так -> True
    """
    stmt = select(Admin).where(Admin.user_name == user_name)
    result = await session.execute(stmt)
    if result.scalars().first():
        return True
    return False


def get_one_month_ago() -> int:
    today = datetime.datetime.now().date()
    result = today - datetime.timedelta(days=30)
    result = result.strftime("%s")
    return int(result)
