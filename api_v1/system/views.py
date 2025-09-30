from typing import Annotated

from fastapi import APIRouter, status
from fastapi.params import Header, Path, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_helper import db_helper
from api_v1.system.crud import (
    issue_new_admin,
    get_admin_by_id,
    admin_delete,
    issue_permission_for_admin,
    delete_permission_for_admin,
)
from api_v1.system.dependencies import (
    request_all_jars,
    request_jar_info,
    get_all_permissions_by_admin,
    protect_same_permission,
)
from api_v1.system.schemas import AdminCreate, AdminDataOut, AdminPermission

router = APIRouter(prefix="/system", tags=["System"])


@router.post(
    "/admin/create",
    response_model=AdminDataOut,
    summary="Створити адміністратора",
    description="Випуск нового адміністратора",
)
async def create_admin(
    data_in: AdminCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Функція створює адміністратора, який зможе керувати інституціями
    """
    return await issue_new_admin(data_in=data_in, session=session)


@router.get(
    "/admin/get_info", response_model=AdminDataOut, summary="Дані про адміністратора"
)
async def get_admin_info(
    admin_id: int, session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    """

    :return: Дані що
    знайшлися про адміністратора з таким ID
    """
    return await get_admin_by_id(admin_id=admin_id, session=session)


@router.delete("/admin/delete", summary="Видалити адміністратора")
async def delete_admin_by_id(
    admin_id: int, session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    """Видалити адміністратора за ID"""
    admin = await get_admin_by_id(admin_id=admin_id, session=session)
    return await admin_delete(admin=admin, session=session)


@router.post(
    "/permission/issue",
    status_code=status.HTTP_201_CREATED,
    summary="Випуск дозволу для адміністратора",
)
async def issue_new_permission(
    admin_id: int,
    permission_type: AdminPermission,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Надання нового дозволу для адміністратора
    :return:
    """
    # Перевірка чи не було випущено дозволу для цього адміністратора
    await protect_same_permission(admin_id, permission_type, session)

    admin = await get_admin_by_id(admin_id=admin_id, session=session)
    return await issue_permission_for_admin(
        admin=admin, permission=permission_type, session=session
    )


@router.get("/admin/my/all_permissions")
async def get_my_permissions():
    """Повернути всі дозволи, які закріплені за адміністратором"""
    pass


@router.get("/admin/all_permissions/{admin_id}", summary="Всі дозволи адміністратора")
async def get_all_permissions(
    admin_id: int, session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    return await get_all_permissions_by_admin(admin_id=admin_id, session=session)


@router.delete("/permission/delete", summary="Видалити дозвіл")
async def permission_delete(
    permission_id: int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Видалення дозволу для певного адміністратора
    """
    return await delete_permission_for_admin(
        permission_id=permission_id, session=session
    )


@router.get(
    "/get_all_jars",
    summary="Всі рахунки",
    description="Повернення всіх рахунків, які закріплені за таким токеном",
)
async def get_client_info(
    api_token: Annotated[str, Header(description="API токен отриманий від Монобанку")],
):
    """
    Повернути всі банки по користувачу з таким АПІ токеном
    <b>ОБМЕЖЕННЯ один запит на 60 секунд</b>
    """
    return await request_all_jars(token=api_token)


@router.get(
    "/get_jar_info/{jar_id}",
    description="Повернення виписки за банківським рахунком певного користувача",
    summary="Виписка за рахунком",
)
async def get_jar_info(
    api_token: Annotated[str, Header(description="API токен отриманий від Монобанку")],
    jar_id: Annotated[
        str, Path(description="Ідентифікатор банки (рахунку) користувача")
    ],
):
    """Повертає останні транзакції по банці (рахунку)"""

    return await request_jar_info(api_token, jar_id)
