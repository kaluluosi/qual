from qual.apps.user.constant import AccountType
from qual.core.database import Base, TimeStampMixin, Mapped, mapped_column


class User(Base, TimeStampMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, comment="用户编号"
    )
    username: Mapped[str] = mapped_column(unique=True, index=True, comment="用户名")
    password: Mapped[str] = mapped_column(comment="二进制哈希密码")
    display_name: Mapped[str] = mapped_column(index=True, comment="显示名")
    mail: Mapped[str] = mapped_column(nullable=True, comment="邮箱")
    account_type: Mapped[str] = mapped_column(
        nullable=False, default=AccountType.local, comment="账户类型"
    )
