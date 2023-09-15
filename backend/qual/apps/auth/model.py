from datetime import datetime
from qual.core.database import Base, TimeStampMixin, Mapped, mapped_column
from .constant import Status, AccountType


class User(Base, TimeStampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, comment="用户编号"
    )
    username: Mapped[str] = mapped_column(
        unique=True, nullable=False, index=True, comment="用户名"
    )
    uid: Mapped[str] = mapped_column(nullable=False, index=True, comment="工号/用户唯一标志")
    name: Mapped[str] = mapped_column(index=True, comment="姓名")
    password: Mapped[bytes] = mapped_column(comment="二进制哈希密码")  # 直接二进制保存了
    email: Mapped[str] = mapped_column(unique=True, nullable=False, comment="邮箱")
    mobile: Mapped[str] = mapped_column(comment="手机号码")
    last_login_at: Mapped[datetime] = mapped_column(comment="最后登录时间")
    avatar: Mapped[str] = mapped_column(comment="头像")
    status: Mapped[Status] = mapped_column(default=Status.active, comment="状态")
    is_staff: Mapped[bool] = mapped_column(
        default=True, nullable=False, comment="是否是雇员"
    )
    account_type: Mapped[AccountType] = mapped_column(
        default=AccountType.local, comment="账户类型"
    )  # 用来区分这个账户是怎么创建的
