from qual.core.database import Base, TimeStampMixin, Mapped, mapped_column


class User(Base, TimeStampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, comment="用户编号"
    )
    username: Mapped[str] = mapped_column(unique=True, index=True, comment="用户名")
    password: Mapped[str] = mapped_column(comment="二进制哈希密码")  # 直接二进制保存了
