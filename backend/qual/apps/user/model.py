import secrets
import uuid
from typing import Self
from sqlalchemy.orm import Mapped, mapped_column
from enum import StrEnum
from qual.core.database import Model
from qual.core.xyapi.security import verify_password, hash_password


class AccountType(StrEnum):
    local = "本地账户"
    xysso = "XYSSO账户"


class User(Model):
    username: Mapped[str] = mapped_column(unique=True, index=True, comment="用户名")
    mail: Mapped[str] = mapped_column(default=None, nullable=True, comment="邮箱")
    password: Mapped[str] = mapped_column(
        default=secrets.token_urlsafe, comment="二进制哈希密码", doc="如果密码为空那么随机生成一个"
    )
    display_name: Mapped[str] = mapped_column(
        default=uuid.uuid4, nullable=True, index=True, comment="显示名"
    )
    account_type: Mapped[str] = mapped_column(
        nullable=False, default=AccountType.local, comment="账户类型"
    )

    def verify_password(self, password: str) -> bool:
        """验证密码"""
        return verify_password(self.password, password)

    def set_password(self, password: str) -> None:
        """设置密码"""
        self.password = hash_password(password)

    @classmethod
    def get_by_username(cls, username: str) -> Self | None:
        """
        通过用户名获取

        Args:
            username (str): 用户名

        Returns:
            Self | None: 如果没找到就返回None
        """
        user = cls.scalar(cls.select.where(cls.username == username))
        return user

    def __repr__(self) -> str:
        return f"<User {self.username}>"
