from enum import IntEnum
from qual.core.database import Model
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey


class DataScope(IntEnum):
    """
    数据权限范围
    """

    self_only = 0  # 自身
    department_and_below = 1
    department_only = 2
    all = 3
    custom = 4


class Role(Model):
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(comment="角色名")
    key: Mapped[str] = mapped_column(unique=True, comment="角色编号")
    sort: Mapped[int] = mapped_column(default=1, comment="排序编号")
    admin: Mapped[bool] = mapped_column(default=False, comment="是否为管理员")

    data_scope: Mapped[int] = mapped_column(
        default=DataScope.self_only, comment="数据权限范围"
    )

    comment: Mapped[str] = mapped_column(nullable=True, comment="备注")
