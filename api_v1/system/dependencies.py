import datetime

import requests

import bcrypt

async def hash_password(password: bytes):
    salt=bcrypt.gensalt()
    password=bcrypt.hashpw(password, salt)
    return password

async def request_info_about_client(token: str):
    api = requests.get(
        "https://api.monobank.ua/personal/client-info", headers={"X-Token": token}
    ).json()
    print("MONO API CALL")
    return api

def get_one_month_ago()->int:
    today = datetime.datetime.now().date()
    result = today - datetime.timedelta(days=30)
    result=result.strftime("%s")
    return int(result)


