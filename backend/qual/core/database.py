import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import Mapped, mapped_column
from qual.core.settings import settings
from qual.core.xyapi.database.sqlalchemy_activerecord import Model as BaseModel


logger = logging.getLogger(__name__)


class Model(BaseModel):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键")

    ...


class OrderMixin:
    """
    支持排序值
    """

    order: Mapped[int] = mapped_column(default=1, autoincrement=True, comment="排序值")


class KeyMixin:
    """
    以字符串key作为主键
    """

    key: Mapped[str] = mapped_column(
        unique=True, index=True, nullable=True, comment="索引key"
    )


engine = create_engine(settings.DB_DSN, echo=settings.DEBUG)
BaseModel.bind(engine)
