from typing import Annotated
from fastapi import Depends
from qual.apps.user.model import User
from qual.apps.auth.authorizations.xysso.router import xysso_bearer
from qual.apps.auth.authorizations.oauth2password.router import oauth2_password_bearer
from qual.core.xyapi.security import AccessTokenPayloadADP
from qual.apps.user.model import User


def authenticate(
    token: AccessTokenPayloadADP,
    _1=Depends(xysso_bearer),
    _2=Depends(oauth2_password_bearer),
):
    """
    认证并返回当前登录的用户

    这个依赖项是用来给 `openapi` 用的， 实际最终AccessTokenPayloadADP起作用。
    后面的依赖项都是用来给 `opanapi` 页面注册认证模式用的。

    Args:
        token (AccessTokenPayloadADP): 访问令牌
        user_dao (UserDAO_ADP): 用户DAO
        _1 (_type_, optional): sso认证. Defaults to Depends(xysso_bearer).
        _2 (_type_, optional): password认证. Defaults to Depends(oauth2_password_bearer).

    Returns:
        _type_: _description_
    """
    user = User.scalar(User.select.where(User.username == token.sub))
    return user


AuthenticateADP = Annotated[User, Depends(authenticate)]
