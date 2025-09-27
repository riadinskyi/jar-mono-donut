from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Header, Path, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_helper import db_helper
from api_v1.system.crud import (
    issue_new_admin,
    get_admin_by_id,
    admin_delete,
    issue_new_permission_for_admin,
)
from api_v1.system.dependencies import request_all_jars, request_jar_info
from api_v1.system.schemas import AdminCreate, AdminDataOut, AdminPermission

router = APIRouter(prefix="/system", tags=["System"])


@router.post("/admin/create", response_model=AdminDataOut)
async def create_admin(
    data_in: AdminCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Функція створює адміністратора який зможе керувати інституціями
    """
    return await issue_new_admin(data_in=data_in, session=session)


@router.get("/admin/get_info", response_model=AdminDataOut)
async def get_admin_info(
    admin_id: int, session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    """

    :param admin_id: Адмін ID, який зареєстровано в базі даних
    :return: Дані що знайшлися про адміністратора з таким ID
    """
    return await get_admin_by_id(admin_id=admin_id, session=session)


@router.delete("/admin/delete")
async def delete_admin_by_id(
    admin_id: int, session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    """Видалити адміністратора за ID"""
    admin = await get_admin_by_id(admin_id=admin_id, session=session)
    return await admin_delete(admin=admin, session=session)


@router.post("/issue_new_permission")
async def issue_new_permission(
    admin_id: int,
    permission_type: AdminPermission,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Надання нового дозволу для адміністратора
    :return:
    """
    admin = await get_admin_by_id(admin_id=admin_id, session=session)
    return await issue_new_permission_for_admin(
        admin=admin, permission=permission_type, session=session
    )


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
