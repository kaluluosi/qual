from contextvars import ContextVar
from contextlib import contextmanager
from typing import Any
from sqlalchemy.orm import Session,DeclarativeBase,declared_attr,MappedAsDataclass,Mapped,mapped_column
from sqlalchemy import Engine,select

class AutoTableNameMixin:
    """
    自动用类名的小写形式做表名
    """
    
    @declared_attr.directive
    @classmethod
    def __tablename__(cls)->str:
        return cls.__name__.lower()
    

class ActiveRecordMixin:
    
    _engine_var = ContextVar[Engine]("engine_var")
    _session_var = ContextVar[Session]("session_var")
    

    @classmethod
    @property
    def engine(cls) -> Engine:
        return cls._engine_var.get()

    @classmethod
    @property
    def session(cls)->Session:
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
    def start_session(cls,begin=False,*args, **kwargs):
        if cls.engine is None:
            raise RuntimeError("No engine bound")
        
        session = Session(cls.engine, *args, **kwargs)
        token = cls._session_var.set(session)
        if begin:
            with session.begin():
                yield session
        else:
            yield session
        cls._session_var.reset(token)
    
    @classmethod
    @property
    def select(cls):
        return select(cls)
    
    @classmethod
    def scalar(cls,stmt:Any):
        return cls.session.scalar(stmt)
    
    @classmethod
    def scalars(cls,stmt:Any):
        return cls.session.scalars(stmt)
    
    @classmethod
    def get(cls,id:Any):
        return cls.session.get(cls,id)
    
    def delete(self):
        """删除是立即发生的
        """
        self.session.delete(self)
    
    def save(self,commit=True):
        self.session.add(self)
        if commit:
            self.session.commit()



        
class Model(DeclarativeBase,ActiveRecordMixin,MappedAsDataclass):
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
    
