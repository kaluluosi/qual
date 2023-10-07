import logging
from datetime import datetime
from qual.core.xyapi.database.sqlalchemy import init_engine
from qual.core.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

logger = logging.getLogger(__name__)

# 引擎的初始化在这里
engine = create_engine(settings.DB_DSN, echo=settings.DEBUG)
init_engine(engine)


class Base(DeclarativeBase):
    """
    ORM模型基类
    """

    ...


class TimeStampMixin:
    """
    审计类，给模型添加审计字段
    """

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, comment="创建时间"
    )

    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime] = mapped_column(comment="删除时间")
