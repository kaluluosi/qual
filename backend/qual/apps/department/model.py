from qual.core.database import Model, OrderMixin, KeyMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from qual.apps.user.model import User


class Department(Model, OrderMixin, KeyMixin):
    actived: Mapped[bool] = mapped_column(default=True, comment="是否激活状态")

    # foreign key
    owner_id: Mapped[int] = mapped_column(ForeignKey(User.id), comment="负责人")
    parent_id: Mapped[int] = mapped_column(
        ForeignKey("department.id"), nullable=True, comment="父部门"
    )

    # relationship
    owner: Mapped[User] = relationship()
    members: Mapped[list[User]] = relationship(
        secondary="userdepartmentassociation", backref="departments"
    )

    parent: Mapped["Department"] = relationship(back_populates="child")
    child: Mapped["Department"] = relationship(back_populates="parent")


class UserDepartmentAssociation(Model):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    department_id: Mapped[int] = mapped_column(ForeignKey(Department.key))
