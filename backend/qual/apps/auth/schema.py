from pydantic import BaseModel, ConfigDict
from .constant import AccountType


class UserBase(BaseModel):
    username: str
    model_config = ConfigDict(from_attributes=True)


class UserRead(UserBase):
    id: int
    account_type: AccountType | None = None


class UserCreate(UserBase):
    password: str
