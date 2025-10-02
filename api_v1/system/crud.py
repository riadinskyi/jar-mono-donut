from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from core import Admin, Permission
from .schemas import AdminCreate
from core.enums import AdminPermission
from .dependencies import check_user_name_availability, get_all_permissions_by_admin
from core.utils import hash_password


async def issue_permission_for_admin(
    admin: Admin, permission: AdminPermission, session: AsyncSession
):
    """
    Випуск дозволу для адміністратора.
    """
    new_permission = Permission(
        permission_type=permission,
        admin_id=admin.id,
    )
    session.add(new_permission)
    await session.commit()
    await session.refresh(new_permission)
    return new_permission


async def delete_permission_for_admin(permission_id: int, session: AsyncSession):
    stmt = delete(Permission).where(Permission.id == permission_id)
    await session.execute(stmt)
    await session.commit()
    return HTTPException(
        status_code=status.HTTP_204_NO_CONTENT, detail="Permission deleted"
    )


async def get_admin_by_id(admin_id: int, session: AsyncSession):
    """
    Retrieves an admin object by its unique identifier from the database. If
    the admin does not exist, an HTTPException with a 404 status code is
    raised. This function is asynchronous and utilizes an asynchronous
    database session.

    :param admin_id: The unique identifier of the admin to be retrieved.
    :type admin_id: int

    :param session: An active asynchronous database session used for querying.
    :type session: AsyncSession

    :return: The retrieved admin object corresponding to the provided admin_id.
    :rtype: Admin

    :raises HTTPException: Raised with a 404 status code if the admin with the
        specified admin_id is not found.
    """
    admin = await session.get(Admin, admin_id)
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found"
        )
    return admin


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


async def admin_delete(admin: Admin, session: AsyncSession):
    # Видалення всіх дозволів, які були закріплені за адміністратором.
    admin_permissions_id = []
    admin_permission_data = await get_all_permissions_by_admin(
        admin_id=admin.id, session=session
    )
    for permission in admin_permission_data:
        admin_permissions_id.append(permission.id)
    for permission_id in admin_permissions_id:
        await delete_permission_for_admin(permission_id=permission_id, session=session)

    # Видалення самого адміністратора
    stmt = delete(Admin).where(Admin.id == admin.id)
    await session.execute(stmt)
    await session.commit()
    return HTTPException(
        status_code=status.HTTP_204_NO_CONTENT,
        detail={
            "admin_details": f"Admin {admin.id} has been deleted",
            "permission_details": f"Permissions: {admin_permissions_id} for admin #{admin.id} has been deleted",
        },
    )
