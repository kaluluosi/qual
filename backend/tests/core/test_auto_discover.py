import qual
import qual.core
from qual.core.xyapi.auto_discover import discover, auto_discover


def test_discover():
    """
    测试模块发现
    """

    modules = discover(qual, "__main__")

    modules = list(modules)

    assert len(modules) == 1
    assert modules[0] == "qual.__main__"

    modules = discover(qual.core, "config*")
    modules = list(modules)

    assert len(modules) == 1
    assert modules[0] == "qual.core.config"


def test_auto_discover():
    """
    测试模块自动发现导入
    """

    modules = auto_discover(qual, "__main__")

    assert len(modules) == 1
    assert "qual.__main__" in modules
