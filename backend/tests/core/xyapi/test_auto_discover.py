import pytest
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


def test_discover_with_name():
    """
    测试模块发现：用模块名
    """
    modules = discover("qual", "__main__")
    modules = list(modules)

    assert len(modules) == 1
    assert modules[0] == "qual.__main__"


def test_discover_with_submodule():
    """
    测试模块发现：子模块导入串
    """
    modules = discover(qual.core, "config*")
    modules = list(modules)

    assert len(modules) == 1
    assert modules[0] == "qual.core.config"


def test_discover_with_submodule_name():
    """
    测试模块发现：用子模块导入串字符
    """
    modules = discover("qual.core", "config*")
    modules = list(modules)

    assert len(modules) == 1
    assert modules[0] == "qual.core.config"


def test_discover_with_no_match():
    """
    测试模块发现：没有匹配的模块
    """
    modules = discover(qual, "__foo_bar")
    modules = list(modules)

    assert len(modules) == 0


def test_discover_with_not_exit_module():
    """
    测试模块发现：不存在的模块名
    """
    with pytest.raises(ModuleNotFoundError):
        modules = discover("??", "config*")
        modules = list(modules)

        assert len(modules) == 0


def test_auto_discover_with_exist():
    """
    测试模块自动发现导入: 存在匹配的模块
    """

    modules = auto_discover(qual, "__main__")

    assert len(modules) == 1
    assert "qual.__main__" in modules


def test_auto_discover_with_not_match():
    """
    测试模块自动发现导入：没有匹配的模块
    """
    modules = auto_discover(qual, "not_exist")

    assert len(modules) == 0


def test_auto_descover_with_not_exist_module():
    """
    测试模块自动发现导入：不存在模块
    """
    with pytest.raises(ModuleNotFoundError):
        auto_discover("??", "not_exist")
