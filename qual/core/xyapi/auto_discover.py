"""
自动发现和导入模块工具
"""
import os
import pkg_resources
from glob import glob
from pathlib import Path
from types import ModuleType
from importlib import import_module


def get_module_dir(module: ModuleType | str):
    """获取module所在的文件路径（绝对路径）

    用例：
    ```python
    dir = get_module_dir(os.path) # <—— 直接用导入语句即可
    dir = get_module_dir("os.path") # <—— 用字符串也可以
    ```


    Args:
        module (ModuleType | str): 包路径/模块路径
    """

    if isinstance(module, str):
        module = import_module(module)

    if not module.__package__:
        raise ModuleNotFoundError(f"模块 {module} 不合法，其 `__package__` 属性为空")

    module_dir = pkg_resources.resource_filename(module.__package__, "")
    return module_dir


def discover(module: ModuleType | str, pattern: str = "*"):
    """扫描发现 `module` 下匹配 `pattern` 的模块文件，返回模块路径。

    NOTE: 不会忽略 `_` `__` 开头的模块，完全依据 `pattern` 来匹配模块。

    用例:
    ```python
    module_paths = discover(os, "_*") # <- 找出 `os` 模块中所有下划线开头的模块

    ```

    Args:
        module (ModuleType | str): _description_
        pattern (str): _description_

    Yields:
        _type_: _description_
    """

    module_dir = get_module_dir(module)
    module_name = os.path.basename(module_dir)
    file_pattern = f"{pattern}.py"

    pattern = os.path.join("**", "*", file_pattern)  # <- 'package/**/*/<file_pattern>

    # glob有个问题 `/**/*` 匹配只能匹配出子目录，无法匹配根目录文件
    # FIXME: 不知道有没有更好的方法，有的话改掉
    files = glob(pattern, root_dir=module_dir, recursive=True)

    # 因此在这里要多做一次根目录文件的匹配
    root_files = glob(file_pattern, root_dir=module_dir, recursive=True)
    files.extend(root_files)

    for file in files:
        path = Path(file)
        yield ".".join([module_name, *path.parts]).replace(".py", "")
