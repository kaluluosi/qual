"""
自动发现和导入模块工具
"""
import fnmatch
import os
import pkg_resources
import logging
from glob import glob
from pathlib import Path
from types import ModuleType
from importlib import import_module

logger = logging.getLogger(__package__)

# 不合法的文件模式，不允许自动发现这些文件
INVALIDE_PATTERN = ("__init__", "__main__")


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
    """
        扫描发现 `module` 下匹配 `pattern` 的模块文件，返回模块路径。

        由于这个函数是用来发现python文件模块的，因此默认匹配 `.py` 文件。
        `pattern` 参数只需要填写文件名的通配符规则即可。

        NOTE: 不会忽略 `_` `__` 开头的模块，完全依据 `pattern` 来匹配模块，没有暗箱操作。

        用例:

        ```python
        module_paths = discover(qual, "__") # <- 找出 `qual` 模块中所有下划线开头的模块
        >> [qual.__init__,...]
        ```

        返回的模块路径一定是完整的包路径，比如如果

        ```python
    module_paths = discover(qual.core, "__") # <- 找出 `qual` 模块中所有下划线开头的模块
        >> [qual.core.__init__, ...] <- 返回的模块路径也是完整的 `qual.core.xxx`
        而不会是 `core.xxx`
        ```

        Args:
            module (ModuleType | str): 模块或模块路径（如：`qual.core`)

            pattern (str): 通配符匹配规则，如 `model*`

            include_root (bool): 是否包括根包目录下的文件. Defaults to False.

        Yields:
            _type_: _description_
    """

    if isinstance(module, ModuleType):
        if not module.__package__:
            raise ModuleNotFoundError(f"模块 {module} 不合法，其 `__package__` 属性为空")
        module_name = module.__package__
    else:
        module_name = module

    module_dir = get_module_dir(module)
    file_pattern = f"{pattern}.py"

    pattern = os.path.join("**", "*", file_pattern)  # <- 'package/**/*/<file_pattern>

    # FIXME: glob有个问题 `/**/*` 匹配只能匹配出子目录，无法匹配根目录文件。
    # 现在只能够再做一个 `root_files` 的匹配把根目录文件匹出来。
    # 不知道有没有更好的方法，有的话改掉。
    files = glob(pattern, root_dir=module_dir, recursive=True)

    # HACK: 因此在这里要多做一次根目录文件的匹配
    root_files = glob(file_pattern, root_dir=module_dir, recursive=True)
    files.extend(root_files)

    for file in files:
        path = Path(file)
        yield ".".join([module_name, *path.parts]).replace(".py", "")


def auto_discover(module: ModuleType | str, pattern: str = "*"):
    """自动发现并导入模块。
    这个函数跟 `discover` 不同的是， `discover` 只发现和返回所有模块路径，这个函数则对所
    有模块执行 `import_module`。

    `pattern` 参数不允许设置为 `__init__` `__main__`。

    Args:
        module (ModuleType | str): 模块或者模块路径

        pattern (str, optional): 模块文件名匹配规则，例如 `model*`. Defaults to "*".

    Returns:
        dict[str,ModuleType]: 导入后的模块字典
    """

    if fnmatch.fnmatch("__init__", pattern) or fnmatch.fnmatch("__main__", pattern):
        raise ValueError(f"不允许自动发现 {pattern}，这个模式会匹配到 {INVALIDE_PATTERN}")

    module_paths = discover(module, pattern)

    modules: dict[str, ModuleType] = {}
    for module_path in module_paths:
        module = import_module(module_path)
        logger.info(f"自动发现: {module_path}")
        modules[module_path] = module

    return modules
