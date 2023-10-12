import typing
from enum import IntEnum
from qual.core.database import Model, KeyMixin, OrderMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

if typing.TYPE_CHECKING:
    from qual.apps.user.model import User


class DataScope(IntEnum):
    """
    数据权限范围
    """

    self_only = 0  # 自身
    department_and_below = 1
    department_only = 2
    all = 3
    custom = 4


class Department(Model, KeyMixin, OrderMixin):
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


class Role(Model, KeyMixin, OrderMixin):
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(comment="角色名")
    admin: Mapped[bool] = mapped_column(default=False, comment="是否为管理员")

    data_scope: Mapped[int] = mapped_column(
        default=DataScope.self_only, comment="数据权限范围"
    )

    comment: Mapped[str] = mapped_column(nullable=True, comment="备注")


class Permission(Model, OrderMixin):
    """
    权限

    Action的集合

    可以指代主菜单入口、页面等

    还可以自嵌套父子权限
    """

    id: Mapped[str] = mapped_column(primary_key=True)

    # relationship
    actions: Mapped["Action"] = relationship(back_populates="permision")


class Action(Model):
    """
    操作

    指代大权限下小操作权限
    """

    name: Mapped[str] = mapped_column(comment="名称")
    value: Mapped[str] = mapped_column(comment="权限值")
    api: Mapped[str] = mapped_column(nullable=True, comment="接口地址")
    method: Mapped[str] = mapped_column(nullable=True, comment="请求方式")

    # foreign key
    permission_id: Mapped[int] = mapped_column(
        ForeignKey(Permission.id), comment="属于哪个权限集"
    )
    # relationship
    permission: Mapped[Permission] = relationship(back_populates="actions")


class Menu(Model, OrderMixin):
    """
    后台管理-侧边导航菜单配置
    """

    icon: Mapped[str] = mapped_column(nullable=True, comment="菜单图标")
    name: Mapped[str] = mapped_column(comment="菜单名称")
    is_link: Mapped[bool] = mapped_column(default=False, comment="是否是外链")
    route_path: Mapped[str] = mapped_column(nullable=True, comment="路由地址")
    component: Mapped[str] = mapped_column(nullable=True, comment="组件地址")
    component_name: Mapped[str] = mapped_column(nullable=True, comment="组件名")
    enabled: Mapped[bool] = mapped_column(default=True, comment="开关状态")
    hidden: Mapped[bool] = mapped_column(default=False, comment="是否隐藏")

    # foreign key
    permission_id: Mapped[int] = mapped_column(
        ForeignKey(Permission.id), comment="绑定的权限id", nullable=True
    )
    # relationship
    permission: Mapped[Permission] = relationship(back_populates="menus")
