from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Header, Query

from api_v1.system.crud import request_info_about_client, request_jar_info

router = APIRouter(prefix="/system")

@router.get("/get_all_jars")
async def get_client_info(monobank_token: str):
    """
    Повернути всі банки по користувачу з таким АПІ токеном
    <b>ОБМЕЖЕННЯ один запит на 60 секунд</b>
    """
    return await request_info_about_client(monobank_token)


@router.get(("/get_jar_info/{jar_id}"))
async def get_jar_info(
        from_time:Annotated[float, Query(
            title="from_time",
            description="початковий час Unix (у секундах)",)],
        jar_id=str,
        api_token: str=Header(),
):

    return await request_jar_info(api_token, jar_id, from_time)

