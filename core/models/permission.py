from core.base import Base
from sqlalchemy import Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from api_v1.system.schemas import AdminPermission


class Permission(Base):
    permission_type: Mapped[AdminPermission] = mapped_column(
        SQLEnum(
            AdminPermission,
            name="permission_type",
            create_constraint=True,
            nullable=False,
        ),
    )
    admin_id: Mapped[int] = mapped_column(ForeignKey("admins.id"), nullable=False)
