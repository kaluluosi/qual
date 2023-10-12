from qual.core.database import Model, OrderMixin, KeyMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from enum import IntEnum


class VariantType(IntEnum):
    text = 0
    number = 1
    date = 2
    datetime = 3
    time = 4
    file = 5
    boolean = 6
    image = 7


class Dictionary(Model, KeyMixin, OrderMixin):
    name: Mapped[str] = mapped_column(unique=True, comment="字典名")
    type: Mapped[int] = mapped_column(default=VariantType.text, comment="值类型")
    enable: Mapped[bool] = mapped_column(default=True, comment="启用/禁用")
    comment: Mapped[str] = mapped_column(default="", comment="备注")

    # relationship
    children: Mapped[list["DictionaryKeyValue"]] = relationship(
        cascade="all,delete-orphan",
        back_populates="parent",
    )

    @classmethod
    def get_by_key(cls, key: str):
        _dict = cls.scalar(cls.select.where(cls.key == key))
        return _dict


class DictionaryKeyValue(Model, OrderMixin):
    id: Mapped[int] = mapped_column(primary_key=True, comment="键值编号")
    name: Mapped[str] = mapped_column(comment="键名")
    value: Mapped[str] = mapped_column(comment="值")
    type: Mapped[int] = mapped_column(default=VariantType.text, comment="值类型")
    enable: Mapped[bool] = mapped_column(default=True, comment="启用/禁用")
    color: Mapped[str] = mapped_column(nullable=True, comment="颜色")

    # foreign key
    parent_id: Mapped[int] = mapped_column(ForeignKey(Dictionary.key))

    # relationship
    parent: Mapped[Dictionary] = relationship(back_populates="children")
