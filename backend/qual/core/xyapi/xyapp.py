from types import ModuleType
from importlib.metadata import distribution
from typing import Callable
from fastapi import FastAPI
from pydantic import BaseModel


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


def _setup_app_info(app: FastAPI, package: ModuleType):
    """用轮子包元数据来设置app信息
    Args:
        app (FastAPI): _description_
    """
    if not package.__package__:
        return

    metadata = _PackageMetadata.get(package.__package__)
    app.title = metadata.name
    app.summary = metadata.summary
    app.description = metadata.description
    app.version = metadata.version
    app.contact = {"name": metadata.author, "email": metadata.author_email}


def init(app: FastAPI, package: ModuleType | None):
    """初始化app
    Args:
        app (FastAPI): _description_
    """

    # 将包元数据写入app
    if package:
        _setup_app_info(app, package)

    for installer in _modules:
        installer(app)

    # 更新依赖注入
    app.dependency_overrides.update(_depends)

    return app


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
