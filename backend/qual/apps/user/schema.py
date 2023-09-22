from pydantic import BaseModel, ConfigDict, EmailStr
from .constant import AccountType


class UserBase(BaseModel):
    username: str
    display_name: str
    model_config = ConfigDict(from_attributes=True)
    account_type: AccountType


class UserRead(UserBase):
    id: int


class UserCreate(UserBase):
    plain_password: str | None = None
    mail: EmailStr | None = None
