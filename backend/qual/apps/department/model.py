import typing

from qual.core.database import Model, OrderMixin, KeyMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

if typing.TYPE_CHECKING:
    from qual.apps.user.model import User


class Department(Model, OrderMixin, KeyMixin):
    owner: Mapped[User] = mapped_column(nullable=True, comment="负责人")
    actived: Mapped[bool] = mapped_column(default=True, comment="是否激活状态")

    # foreign key
    parent_id: Mapped[int] = mapped_column(
        ForeignKey("department.id"), nullable=True, comment="父部门"
    )

    # relationship
    users: Mapped[list[User]] = relationship(
        secondary="userdepartmentassociation", backref="departments"
    )

    parent: Mapped["Department"] = relationship(back_populates="child")
    child: Mapped["Department"] = relationship(back_populates="parent")


class UserDepartmentAssociation(Model):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey(Department.key))
