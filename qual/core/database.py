import importlib
import os
import glob
import pkg_resources
import qual
from types import ModuleType
from qual.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


engine = create_engine(settings.DB_DSN)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    ...


def auto_discover_models(module: ModuleType):
    """自动发现module下所有的模型然后导入

    `Alembic` 存在一个问题就是如果继承 `DeclarativeBase` 的 `Model` 没有被导入过，
    那么 `Alembic` 就无法发现模型。

    Args:
        module (ModuleType): _description_
    """

    # 遍历 qual.apps 模块下的所有单文件模块，找出名字以 model开头的py模块，然后调用
    # importlib.import_module导入

    # 找出包的父目录
    package_name = module.__package__
    if not package_name:
        return

    pkg_path = pkg_resources.resource_filename(package_name, "")

    pkg_basedir = os.path.dirname(pkg_path)
    old_cwd = os.getcwd()

    os.chdir(pkg_basedir)

    pattern = os.path.join(qual.__package__, "**", "model*.py")

    # todo: 以后改用logger打印
    print("扫描model", pattern, pkg_basedir)

    for module_path in glob.glob(pattern, recursive=True):
        module_name = module_path.replace("\\", ".")[:-3]
        importlib.import_module(module_name)
        # todo: 以后用logger打印
        print(f"发现Model文件 {module_name}")

    os.chdir(old_cwd)
