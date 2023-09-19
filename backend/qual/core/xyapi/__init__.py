"""
xyapi这个模块是负责提供以下功能:
[1]: 自动发现 —— 解决Alembic无法自动发现项目中所有Sqlalchemy模型定义问题。
[2]: 

"""

from .xyapp import init, installer, initializer, FastAPI
from .auto_discover import auto_discover

__all__ = ["init", "installer", "auto_discover", "initializer", "FastAPI"]
