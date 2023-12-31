from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr, Field
from .model import AccountType


class UserRead(BaseModel):
    id: int
    username: str
    display_name: str
    account_type: AccountType
    password: SecretStr
    mail: EmailStr | None = None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    display_name: str
    password: str
    mail: EmailStr | None = None
    account_type: AccountType | None = Field(default=AccountType.local)

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    display_name: str | None = None
    mail: EmailStr | None = None
    model_config = ConfigDict(from_attributes=True)
