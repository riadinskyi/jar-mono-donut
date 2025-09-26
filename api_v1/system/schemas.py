from pydantic import BaseModel
from enum import Enum


class AdminPermission(str, Enum):
    read_order = "read_order"
    create_order = "create_order"
    edit_order = "edit_order"
    delete_order = "delete_order"

    read_admin = "read_admin"
    issue_new_admin = "issue_new_admin"
    edit_admin = "edit_admin"
    delete_admin = "delete_admin"

    issue_new_permission = "issue_new_permission"
    edit_permission = "edit_permission"
    revoked_permission = "revoked_permission"


class AdminBase(BaseModel):
    user_name: str
    name: str
    password: str


class AdminCreate(AdminBase):
    permission_id: int


class AdminDataOut(BaseModel):
    id: int
    name: str
