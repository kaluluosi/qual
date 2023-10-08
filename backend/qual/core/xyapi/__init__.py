"""
xyapi这个模块是负责提供以下功能:
[1]: 自动发现 —— 解决Alembic无法自动发现项目中所有Sqlalchemy模型定义问题。

"""

from .xyapp import init, installer, FastAPI
from .auto_discover import auto_discover
from .settings import BaseSettings
from .exception import (
    HttpExceptionModel,
    NotFoundError,
    ExistedError,
    JWTUnauthorizedError,
)
from .security import AccessTokenPayloadADP, RefreshTokenPayloadADP, NeedScope, Scope

__all__ = [
    "init",
    "installer",
    "auto_discover",
    "FastAPI",
    "BaseSettings",
    "HttpExceptionModel",
    "NotFoundError",
    "ExistedError",
    "JWTUnauthorizedError",
    "AccessTokenPayloadADP",
    "RefreshTokenPayloadADP",
    "NeedScope",
    "Scope",
]
