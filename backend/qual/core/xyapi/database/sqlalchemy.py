import logging
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import Engine
from contextvars import ContextVar

logger = logging.getLogger(__name__)

_engine_var = ContextVar[Engine]("engine")
_async_engine_var = ContextVar[AsyncEngine]("async_engine")


def init_engine(engine: Engine | AsyncEngine):
    if isinstance(engine, Engine):
        _engine_var.set(engine)
        logger.debug(f"初始化引擎 {engine}")
    elif isinstance(engine, AsyncEngine):
        _async_engine_var.set(engine)
        logger.debug(f"初始化异步引擎 {engine}")


def _session():
    engine = _engine_var.get()
    if engine is None:
        raise RuntimeError("没有初始化引擎，请用 `create_engine` 创建一个引擎，然后调用 `init_engine`。")

    with Session(engine) as session:
        with session.begin():
            logger.debug(f"开始 session {session}")
            yield session


EngineADP = Annotated[Engine, Depends(_engine_var.get, use_cache=True)]
SessionADP = Annotated[Session, Depends(_session, use_cache=True)]


async def _async_session():
    engine = _async_engine_var.get()
    if engine is None:
        raise RuntimeError(
            "没有初始化异步引擎，请用 `create_async_engine` 创建一个引擎，然后调用 `init_engine`。"
        )

    async with AsyncSession(engine) as session:
        async with session.begin():
            logger.debug(f"开始 async session {session}")
            yield session


AsyncEngineADP = Annotated[Engine, Depends(_async_engine_var.get, use_cache=True)]
AsyncSessionADP = Annotated[AsyncSession, Depends(_async_session, use_cache=True)]
