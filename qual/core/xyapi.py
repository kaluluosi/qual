import pkg_resources
from importlib.metadata import distribution
from typing import Callable
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import qual
from qual.core.config import settings

"""
用来注册和统一安装模块
"""

InstallFunction = Callable[[FastAPI], None]

_modules = set()
_depends: dict[Callable, Callable] = {}


class _PackageMetadata(BaseModel):
    """
    包元数据，读取自 poetry的 pyproject.toml 内的元数据。
    """

    name: str
    summary: str
    description: str
    version: str
    author: str
    author_email: str

    @classmethod
    def get(cls, package_name: str):
        dist = distribution(package_name)
        return cls.model_validate(dist.metadata.json)


def _setup_app_info(app: FastAPI):
    """用包元数据来设置app信息
    Args:
        app (FastAPI): _description_
    """
    metadata = _PackageMetadata.get(qual.__package__)
    app.title = metadata.name
    app.summary = metadata.summary
    app.description = metadata.description
    app.version = metadata.version
    app.contact = {"name": metadata.author, "email": metadata.author_email}


def init(app: FastAPI):
    """初始化app
    Args:
        app (FastAPI): _description_
    """

    # 挂上静态文件代理，env有配置就优先使用，不然就用包内部的静态目录
    static_dir = settings.STATIC_PATH or pkg_resources.resource_filename(
        qual.__package__, "static"
    )
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    # 将包元数据写入app
    _setup_app_info(app)

    for installer in _modules:
        installer(app)

    # 更新依赖注入
    app.dependency_overrides.update(_depends)


def register(func: InstallFunction):
    """注册模块安装函数
    Args:
        func (InstallFunction): 安装函数
    """
    _modules.add(func)


def dependency(depend: Callable, override: Callable):
    """注册依赖注入

    Args:
        depend (Callable): 抽象依赖类
        override (Callable): 具体依赖类
    """
    _depends[depend] = override
