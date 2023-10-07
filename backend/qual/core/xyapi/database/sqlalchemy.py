import logging
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import Engine
from contextvars import ContextVar
from contextlib import contextmanager, asynccontextmanager

logger = logging.getLogger(__name__)

_engine_var = ContextVar[Engine]("engine")
_async_engine_var = ContextVar[AsyncEngine]("async_engine")


def init_engine(engine: Engine | AsyncEngine):
    """
    初始化引擎

    这个函数的主要作用是将引擎设置到上下文变量（线程安全的全局变量）

    之所以要让用户来传 `engine` 是因为 `sqlalchemy` 的同步异步 `engine` 是
    两个函数创建的，`engine` 创建函数还有很多选项参数，因此我不想要控制创建过程。

    用例：
    ```python
    # database.py
    engine = create_engine(settings.DB_DSN, echo=settings.DEBUG)
    init_engine(engine) # <- 传engine进去
    ```

    Args:
        engine (Engine | AsyncEngine): _description_
    """

    if isinstance(engine, Engine):
        _engine_var.set(engine)
        logger.debug(f"初始化引擎 {engine}")
    elif isinstance(engine, AsyncEngine):
        _async_engine_var.set(engine)
        logger.debug(f"初始化异步引擎 {engine}")


@contextmanager
def create_session():
    """
    创建同步会话

    这个函数创建的会话是个上下文管理器，而且开启了begin自动提交。

    用例：
    ```python
    with create_session() as session:
        # do something

        # 退出 async with 的时候会自动 commit，并且关闭session

    ```

    Raises:
        RuntimeError: engine没有初始化

    Yields:
        Session: 会话
    """

    yield _create_session()


def _create_session():
    engine = _engine_var.get()
    if engine is None:
        raise RuntimeError("没有初始化引擎，请用 `create_engine` 创建一个引擎，然后调用 `init_engine` 设置。")
    session = Session(engine)

    with session:
        with session.begin():
            logger.debug(f"开始 session {session}")
            yield session


EngineADP = Annotated[Engine, Depends(_engine_var.get, use_cache=True)]
SessionADP = Annotated[Session, Depends(_create_session, use_cache=True)]


@asynccontextmanager
async def create_async_session():
    yield _create_async_session()


async def _create_async_session():
    """
    创建异步会话

    这个函数创建的异步会话是个上下文管理器，而且开启了begin自动提交。

    用例：
    ```python
    async with create_async_session() as session:
        # do something

        # 退出 async with 的时候会自动 commit，并且关闭session

    ```

    Raises:
        RuntimeError: engine没有初始化

    Yields:
        AsyncSession: 异步会话
    """
    engine = _async_engine_var.get()
    if engine is None:
        raise RuntimeError(
            "没有初始化异步引擎，请用 `create_async_engine` 创建一个引擎，然后调用 `init_engine`。"
        )
    session = AsyncSession(_async_engine_var.get())

    async with session:
        async with session.begin():
            logger.debug(f"开始 async session {session}")
            yield session


AsyncEngineADP = Annotated[Engine, Depends(_async_engine_var.get, use_cache=True)]
AsyncSessionADP = Annotated[
    AsyncSession, Depends(_create_async_session, use_cache=True)
]
