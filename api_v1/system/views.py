from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Header, Path, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_helper import db_helper
from api_v1.system.crud import (
    request_jar_info,
    request_all_jars,
    issue_new_admin,
    get_admin_by_id,
)
from api_v1.system.schemas import AdminCreate, AdminDataOut

router = APIRouter(prefix="/system", tags=["System"])


@router.post("/create-admin", response_model=AdminDataOut)
async def create_admin(
    data_in: AdminCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Функція створює адміністратора який зможе керувати інституціями
    """
    return await issue_new_admin(data_in=data_in, session=session)


@router.get("/get_admin_info", response_model=AdminDataOut)
async def get_admin_info(
    admin_id: int, session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    return await get_admin_by_id(admin_id=admin_id, session=session)


@router.get("/get_all_jars")
async def get_client_info(
    api_token: Annotated[str, Header(description="API токен отриманий від Монобанку")],
):
    """
    Повернути всі банки по користувачу з таким АПІ токеном
    <b>ОБМЕЖЕННЯ один запит на 60 секунд</b>
    """
    return await request_all_jars(token=api_token)


@router.get("/get_jar_info/{jar_id}")
async def get_jar_info(
    api_token: Annotated[str, Header(description="API токен отриманий від Монобанку")],
    jar_id: Annotated[
        str, Path(description="Ідентифікатор банки (рахунку) користувача")
    ],
):
    """Повертає транзакції по банці за останні місяць"""

    return await request_jar_info(api_token, jar_id)
