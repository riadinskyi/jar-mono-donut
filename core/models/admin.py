
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


from core.base import Base

class Admin(Base):
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    permission_id: Mapped[int] = mapped_column(nullable=True) # todo Foreign key to Permission table