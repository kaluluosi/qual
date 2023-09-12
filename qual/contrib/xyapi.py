from importlib.metadata import distribution
from typing import Callable
from fastapi import FastAPI
"""
用来注册和统一安装模块
"""

InstallFunction = Callable[[FastAPI], None]
    
_modules = set()
_depends:dict[Callable,Callable] = {}

def init(app:FastAPI):
    """将所有模块初始化安装到app上
    Args:
        app (FastAPI): _description_
    """
    for installer in _modules:
        installer(app)
    
    # 更新依赖注入
    app.dependency_overrides.update(_depends)
    
def register( func:InstallFunction):
    """注册模块安装函数
    Args:
        func (InstallFunction): 安装函数
    """
    _modules.add(func)
    
def dependency(depend:Callable, override:Callable):
    _depends[depend] = override
    
    