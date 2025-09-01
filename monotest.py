import json

import requests
from requests import get
from requests.exceptions import HTTPError
import datetime

api_token = "uppewGFfBYH0AQzHGhYsUStMWuJ2_e_4DWcxHCvedTk0"


def get_info():
    api = get(
        "https://api.monobank.ua/personal/client-info", headers={"X-Token": api_token}
    ).json()
    print("MONO API CALL")
    return api


# print(get_info())


jar_name = "Подяка за продукти"
jar_account = "9As0GboMjewDjqB3SMMIdFz1mV_VHxQ"
date_from = datetime.datetime(2025, 7, 25).timestamp()
date_to = datetime.datetime.now().timestamp()


def get_jar_info(jar_id, from_time, to_time):
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


def save_jar_to_json(data, jar_id, from_time, to_time, prefix="jar_statement"):
    """
    Зберігає відповідь API у JSON-файл зі структурованим іменем

    Параметри:
    data -- дані для збереження (словник або список)
    jar_id -- ідентифікатор банки
    from_time -- початковий час Unix (у секундах)
    to_time -- кінцевий час Unix (у секундах)
    prefix -- префікс для імені файлу (за замовчуванням "jar_statement")

    Повертає:
    Шлях до збереженого файлу
    """
    # Конвертуємо час у читабельний формат для імені файлу
    from_str = datetime.utcfromtimestamp(from_time).strftime("%Y%m%d_%H%M")
    to_str = datetime.utcfromtimestamp(to_time).strftime("%Y%m%d_%H%M")

    # Генеруємо унікальне ім'я файлу
    filename = f"{prefix}_{jar_id}_{from_str}_to_{to_str}.json"

    # Зберігаємо дані у файл
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Дані збережено у файл: {filename}")
    return filename


print(date_from)
# print(get_info())
print(get_jar_info(jar_id=jar_account, from_time=date_from, to_time=date_to))
