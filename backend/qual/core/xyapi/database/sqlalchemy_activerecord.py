from contextvars import ContextVar
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Self
from sqlalchemy.orm import (
    Session,
    DeclarativeBase,
    declared_attr,
    Mapped,
    mapped_column,
)
from sqlalchemy import Engine, ScalarResult, select


class AutoTableNameMixin:
    """
    自动用类名的小写形式做表名
    """

    # 官方文档说是这是用于类的配置属性（dunder）
    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class AuditMixin:
    """
    审计字段
    """

    create_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )


class ActiveRecordMixin:
    _engine_var = ContextVar[Engine]("engine_var")
    _session_var = ContextVar[Session]("session_var")

    @classmethod
    @property
    def engine(cls) -> Engine:
        return cls._engine_var.get()

    @classmethod
    @property
    def session(cls) -> Session:
        """
        会尝试从上下文中获取session，如果上下文没有session，
        那么就自己创建一个。

        Returns:
            Session: _description_
        """
        try:
            return cls._session_var.get()
        except LookupError:
            session = Session(cls.engine)
            cls._session_var.set(session)
            return session

    @classmethod
    def bind(cls, engine: Engine):
        cls._engine_var.set(engine)

    @classmethod
    @contextmanager
    def start_session(cls, begin=False, *args, **kwargs):
        if cls.engine is None:
            raise RuntimeError("No engine bound")

        session = Session(cls.engine, *args, **kwargs)
        token = cls._session_var.set(session)
        if begin:
            with session.begin():
                yield session
                print("提交")
        else:
            yield session
        cls._session_var.reset(token)

    @classmethod
    @property
    def select(cls):
        return select(cls)

    @classmethod
    def scalar(cls, stmt: Any) -> Self | None:
        return cls.session.scalar(stmt)

    @classmethod
    def scalars(cls, stmt: Any) -> ScalarResult[Self]:
        return cls.session.scalars(stmt)

    @classmethod
    def query(cls, stmt: Any):
        return cls.session.query(stmt)

    @classmethod
    def get_by_pk(cls, primary_key: Any) -> Self | None:
        """
        通过主键获取

        Args:
            primary_key (Any): 主键

        Returns:
            Self | None: _description_
        """
        return cls.session.get(cls, primary_key)

    def delete(self, commit=True):
        self.session.delete(self)
        if commit:
            self.session.commit()

    def save(self, commit=True):
        self.session.add(self)
        if commit:
            self.session.commit()

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.save()

    @classmethod
    def is_empty_table(cls):
        data = cls.scalar(cls.select.where())
        return data is None


class Model(
    DeclarativeBase,
    ActiveRecordMixin,
    AuditMixin,
    AutoTableNameMixin,
):
    """
    模型基类

    用例：
    ```python
    # 单数据库直接继承即可

    class User(Model):
        id:Mapped[int] = mapped_column(primary_key=True)


    # 多数据库你需要派生一个抽象Model
    class DB1_Model(Model):
        __abstract__ = True
        metadata = MetaData() # 这里创建DB1_Model自己的metadata对象，这样才不会跟基类Model的metadata混淆

    ```

    Args:
        DeclarativeBase (_type_): _description_
        _Mixin (_type_): _description_
    """

    ...
