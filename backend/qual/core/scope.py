from qual.core.xyapi.security import ScopeBase, register_scope


class Scope(ScopeBase):
    """
    Scope定义
    """

    all = "all"
    test = "测试"


register_scope(Scope)
