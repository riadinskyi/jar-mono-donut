from datetime import datetime

import requests
from requests.exceptions import HTTPError
from .dependencies import get_one_month_ago, request_info_about_client


async def request_all_jars(token: str):
    request= await request_info_about_client(token=token)
    all_jars=[]
    for jar in request["jars"]:
        all_jars.append(jar)
    return all_jars



async def request_jar_info(api_token,jar_id, from_time=get_one_month_ago(), to_time=datetime.now().timestamp()):
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
