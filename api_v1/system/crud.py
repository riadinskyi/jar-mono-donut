from datetime import datetime
from fastapi import HTTPException, status
import requests
from requests.exceptions import HTTPError
from sqlalchemy.ext.asyncio import AsyncSession

from core import Admin
from .schemas import AdminCreate
from .dependencies import (
    get_one_month_ago,
    request_info_about_client,
    check_user_name_availability,
)
from core.utils import hash_password


async def issue_new_admin(data_in: AdminCreate, session: AsyncSession):
    hs_pw = await hash_password(data_in.password.encode("utf-8"))
    check_user_name = await check_user_name_availability(
        user_name=data_in.user_name, session=session
    )
    if check_user_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user_name already exists",
        )
    new_admin = Admin(
        user_name=data_in.user_name,
        name=data_in.name,
        password=hs_pw,
        permission_id=data_in.permission_id,
    )
    session.add(new_admin)
    await session.commit()
    await session.refresh(new_admin)
    return new_admin


async def issue_permission_for_admin(permission_id: int, session: AsyncSession):
    """
    Випуск дозволу для адміна, щоб керувати базами даних, можна використовувати
    для ручного так і для автоматичного створення
    """

    pass


async def request_all_jars(token: str):
    request = await request_info_about_client(token=token)
    all_jars = []
    for jar in request["jars"]:
        all_jars.append(jar)
    return all_jars


async def request_jar_info(
    api_token, jar_id, from_time=get_one_month_ago(), to_time=datetime.now().timestamp()
):
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

    # Перевірка коректності проміжку
    if from_time > to_time:
        raise ValueError("Початковий час не може бути пізніше кінцевого")

    # Конвертація у цілі числа
    from_time = int(from_time)
    to_time = int(to_time)

    # Корекція проміжку, якщо він перевищує ліміт
    actual_to = min(to_time, from_time + max_interval)

    url = f"https://api.monobank.ua/personal/statement/{jar_id}/{from_time}/"

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


async def admin_delete(admin: Admin, session: AsyncSession):
    pass
