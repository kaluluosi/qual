import os
import qual
from qual.core.xyapi.auto_discover import discover


def test_discover():
    modules = discover(qual, "*")

    modules = list(modules)

    assert len(modules) == 1
    assert modules[0] == "qual.__main__"
