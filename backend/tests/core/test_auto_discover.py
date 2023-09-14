import qual
import qual.core
from qual.core.xyapi.auto_discover import discover


def test_discover():
    modules = discover(qual, "__main__")

    modules = list(modules)

    assert len(modules) == 1
    assert modules[0] == "qual.__main__"

    modules = discover(qual.core, "config*")
    modules = list(modules)

    assert len(modules) == 1
    assert modules[0] == "qual.core.config"


def test_auto_discover():
    ...
