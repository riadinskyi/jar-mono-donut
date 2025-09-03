from pydantic import BaseModel


class AdminBase(BaseModel):
    name: str
    password: str


class AdminCreate(AdminBase):
    permission_id: int

class AdminDataOut(BaseModel):
    id: int
    name: str
