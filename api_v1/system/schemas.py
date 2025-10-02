from pydantic import BaseModel
from core.enums import AdminPermission


class AdminBase(BaseModel):
    user_name: str
    name: str
    password: str


class AdminCreate(AdminBase):
    permission_id: int


class AdminDataOut(BaseModel):
    id: int
    name: str
