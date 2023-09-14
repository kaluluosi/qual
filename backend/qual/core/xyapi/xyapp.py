import logging
from types import ModuleType
from importlib.metadata import distribution
from typing import Callable
from fastapi import FastAPI
from pydantic import BaseModel
from .auto_discover import auto_discover

logger = logging.getLogger(__name__)

InstallFunction = Callable[[FastAPI], None]

_modules = dict[str, InstallFunction]()
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


def _setup_app_info(app: FastAPI, module: ModuleType):
    """用轮子包元数据来设置app信息
    Args:
        app (FastAPI): _description_
    """
    if not module.__package__:
        raise ModuleNotFoundError(f"模块 {module} 不属于任何包")

    metadata = _PackageMetadata.get(module.__package__)
    app.title = metadata.name
    app.summary = metadata.summary
    app.description = metadata.description
    app.version = metadata.version
    app.contact = {"name": metadata.author, "email": metadata.author_email}


def init(app: FastAPI, package: ModuleType):
    """初始化app
    Args:
        app (FastAPI): _description_
    """

    # 将包元数据写入app
    if package:
        _setup_app_info(app, package)

    # 自动发现app模块
    # 将模块的install函数放在 `__app__` 并用 `register` 装饰
    # NOTE: 这是个约定
    logger.debug("=" * 10 + " 开始自动发现app模块 " + "=" * 10)
    auto_discover(package, "__app__")

    # 遍历所有安装函数安装app
    logger.debug("=" * 10 + " 开始安装app " + "=" * 10)
    for name, installer in _modules.items():
        logger.debug(f"执行安装app：{name}.{installer.__qualname__}")
        installer(app)

    # 更新依赖注入
    app.dependency_overrides.update(_depends)

    return app


def register(name: str):
    """注册模块安装函数
    Args:
        func (InstallFunction): 安装函数
    """

    def _wrapper(func: InstallFunction):
        logger.debug(f"注册app安装器：{name}.{func.__qualname__} ")
        _modules[name] = func

    return _wrapper


def dependency(depend: Callable, override: Callable):
    """注册依赖注入

    Args:
        depend (Callable): 抽象依赖类
        override (Callable): 具体依赖类
    """
    _depends[depend] = override
