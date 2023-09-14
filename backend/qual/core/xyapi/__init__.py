"""
xyapi这个模块是负责提供以下功能:
[1]: 自动发现 —— 解决Alembic无法自动发现项目中所有Sqlalchemy模型定义问题。
[2]: 

"""

from .xyapp import init, register
from .auto_discover import auto_discover

__all__ = ["init", "register", "auto_discover"]
