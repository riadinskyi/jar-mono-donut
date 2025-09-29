import datetime
import requests
from fastapi import HTTPException, status

from requests.exceptions import HTTPError

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.system.schemas import AdminPermission
from core import Permission
from core.models.admin import Admin


async def get_all_permissions_by_admin(
    admin_id: int,
    session: AsyncSession,
    admin_id: int,
):
    """
    Повернути всі видані дозволи для певного адміністратора.
    """
    stmt = select(Permission).where(Permission.admin_id == admin_id)
    result = await session.execute(stmt)
    permissions = result.scalars().all()
    return permissions


async def protect_same_permission(
    admin_id: int, permission: AdminPermission, session: AsyncSession
):
    """
    Checks if the given permission is already assigned. If it is, raises a 409 Conflict 🚫.
    """
    all_permissions = await get_all_permissions_by_admin(
        admin_id=admin_id, session=session
    )

    permission_exists = any(p.permission_type == permission for p in all_permissions)

    if permission_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Permission '{permission.name}' already exists for admin ID {admin_id}. Duplication avoided.",
        )


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


async def request_all_jars(token: str):
    request = await request_info_about_client(token=token)
    all_jars = []
    for jar in request["jars"]:
        all_jars.append(jar)
    return all_jars


async def request_jar_info(api_token, jar_id, from_time=None, to_time=None):
    """
    Отримує виписку по банці за вказаний проміжок часу

    Параметри:
    jar_id -- ідентифікатор банки
    from_time -- початковий час Unix (у секундах, ціле число)
    to_time -- кінцевий час Unix (у секундах, ціле число)

    Повертає:
    Список транзакцій у форматі JSON

    Викидає:
    ValueError -- при некоректному проміжку часу
    HTTPError -- при помилці запиту до API
    """
    # Максимальний дозволений проміжок (31 доба + 1 година)
    max_interval = 2682000

    # Значення за замовчуванням для часових меж
    if from_time is None:
        from_time = get_one_month_ago()
    if to_time is None:
        to_time = int(datetime.datetime.now().timestamp())

    # Перевірка коректності проміжку
    if from_time > to_time:
        raise ValueError("Початковий час не може бути пізніше кінцевого")

    # Конвертація у цілі числа
    from_time = int(from_time)
    to_time = int(to_time)

    # Корекція проміжку, якщо він перевищує ліміт
    actual_to = min(to_time, from_time + max_interval)

    url = f"https://api.monobank.ua/personal/statement/{jar_id}/{from_time}/{actual_to}"

    try:
        response = requests.get(url, headers={"X-Token": api_token})
        response.raise_for_status()  # Перевірка статусу відповіді

        print(f"MONO API CALL JAR: {jar_id} ({from_time} - {actual_to})")
        return response.json()

    except HTTPError as http_err:
        # Додатковий вивід інформації про помилку
        error_details = {
            "status_code": response.status_code,
            "url": response.url,
            "response": response.text[:500],  # Перші 500 символів відповіді
        }
        print(f"HTTP помилка: {http_err}\nДеталі: {error_details}")
        raise
    except Exception as err:
        print(f"Інша помилка: {err}")
        raise
