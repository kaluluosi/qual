import logging
from datetime import datetime
from qual.core.xyapi.database.sqlalchemy import init_engine
from qual.core.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

logger = logging.getLogger(__name__)

# 引擎的初始化在这里
# XXX: 在这里创建engine会导致engine这个变量不是线程/协程安全的，但是好像也不影响使用。
# 所以实际的问题是：engine对象应该只有一个地方可以公开访问，目前只能在这里。
engine = create_engine(settings.DB_DSN, echo=settings.DEBUG)
# XXX：init_engine只是简单的将 engine 对象注册到 `qual.core.xyapi.database.sqlalchemy`
# 的上下文变量中，避免该模块被调用时线程/协程不安全，同时解除耦合。
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
