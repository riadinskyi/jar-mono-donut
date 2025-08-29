from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Header, Path
from api_v1.system.crud import request_info_about_client, request_jar_info

router = APIRouter(prefix="/system",tags=["System"])

@router.get("/get_all_jars")
async def get_client_info(
        api_token:Annotated[str,Header(description="API токен отриманий від Монобанку")]
):
    """
    Повернути всі банки по користувачу з таким АПІ токеном
    <b>ОБМЕЖЕННЯ один запит на 60 секунд</b>
    """
    return await request_info_about_client(api_token)


@router.get("/get_jar_info/{jar_id}")
async def get_jar_info(
        api_token:Annotated[str,Header(description="API токен отриманий від Монобанку")],
        jar_id:Annotated[str, Path(description="Ідентифікатор банки (рахунку) користувача")],
):
    """Повертає транзакції по банці за останні місяць"""

    return await request_jar_info(api_token, jar_id)

