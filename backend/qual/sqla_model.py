from contextvars import ContextVar
from contextlib import contextmanager
from typing import Any, Literal, Optional, Union
from sqlalchemy.orm import Session,DeclarativeBase,Mapped,mapped_column
from sqlalchemy import Connection, MetaData, create_engine,Engine,select

class _Mixin:
    
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

        
class Model(DeclarativeBase,_Mixin):
    ...
    

class AModel(Model):
    __abstract__ = True
    metadata = MetaData()


class User(AModel):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(nullable=False)
    email:Mapped[str] = mapped_column(nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"
    
engine = create_engine("sqlite:///:memory:", echo=True)
AModel.bind(engine)
AModel.metadata.create_all(engine)


with User.start_session(True) as session:
    user = User(name="John", email="john@example.com")
    user.save()
    
    
with User.start_session(True) as session:
    users = User.scalars(User.select.where())
    print(users)
    
tom = User(name="Tom", email="tom@example.com")
marry = User(name="Marry", email="Marry@example.com")

tom.save()
marry.save()

User.session.commit()


users = User.session.scalars(User.select.where()).all()

print(users)

tom.delete()

users = User.session.scalars(User.select.where()).all()

print(users)
