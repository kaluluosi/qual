from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from .constant import AccountType, Status


class UserBase(BaseModel):
    username: str
    uid: str = ""
    name: str = "nonamed"
    email: str = ""
    mobile: str = ""
    avatar: str = ""
    status: Status = Status.active
    is_staff: bool = True
    account_type: AccountType = AccountType.local

    model_config = ConfigDict(from_attributes=True)


class UserOut(UserBase):
    id: int
    last_login_at: datetime | None = None


class UserIn(UserBase):
    password: bytes
