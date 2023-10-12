import typing

from qual.core.database import Model
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

if typing.TYPE_CHECKING:
    from qual.apps.user.model import User


class Department(Model):
    id: Mapped[str] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(nullable=True, comment="部门标识")

    sort: Mapped[int] = mapped_column(default=1, comment="排序编号")


class UserDepartmentAssocation(Model):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey(Department.id))
