"""
安全认证相关

AccessToken的创建和解析

"""

import enum
from typing import Annotated, Any, Self
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import (
    HTTPAuthorizationCredentials,
    SecurityScopes,
    HTTPBearer,
)
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from contextvars import ContextVar
from .settings import BaseSettings


# region 密码

# XXX: 写死了,以后不知道要不要改为配置的
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    哈希密码

    Args:
        plain_password (str): 明文密码

    Returns:
        str: 哈希字符串
    """
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    校验密码

    Args:
        plain_password (str): 明文密码
        hashed_password (str): 哈希密码

    Returns:
        bool: 匹配返回 True，不匹配返回 False
    """
    return _pwd_context.verify(plain_password, hashed_password)


# endregion


# region Token


class JWTUnauthorizedError(HTTPException):
    def __init__(
        self, detail: Any = None, scopes: SecurityScopes | None = None
    ) -> None:
        if scopes:
            super().__init__(
                status.HTTP_401_UNAUTHORIZED,
                detail,
                headers={"WWW-Authenticate": f"Bearer scopes={scopes.scope_str}"},
            )
        else:
            super().__init__(
                status.HTTP_401_UNAUTHORIZED,
                detail,
                headers={"WWW-Authenticate": "Bearer"},
            )


class Payload(BaseModel):
    """
    Token的负载部分
    """

    iss: str = Field(default="", description="签发人")
    exp: datetime = Field(default_factory=datetime.utcnow, description="截止日期，时间戳")
    sub: str = Field(default="", description="主题，负载数据")
    aud: list[str] = Field(default_factory=list, description="受众")
    nbf: datetime = Field(default_factory=datetime.utcnow, description="签发时间，时间戳")
    jti: str = Field(default="", description="编号")
    scopes: list[str] = Field(default_factory=list, description="权限范围")

    @classmethod
    def from_jwt(cls, token: str) -> Self:
        """
        从token字符串中解析出负载

        解析的过程中也会检查过期，如果过期会抛出 ExpiredSignatureError

        Args:
            token (str): Bearer <token str> 的 <token str> 部分

        Returns:
            Self: payload对象
        """
        settings = BaseSettings()
        payload = jwt.decode(
            token, key=settings.JWT_SECRET, algorithms=settings.JWT_ALGORITHM
        )
        payload = cls.model_validate(payload)
        return payload

    def to_jwt(self, expires_min: int = 15) -> str:
        """
        将payload加密成Token串

        Args:
            payload (Self): _description_
            expires_min (int, optional): _description_. Defaults to 15.

        Returns:
            str: _description_
        """

        settings = BaseSettings()

        to_encode = self.model_copy()
        to_encode.exp = datetime.utcnow() + timedelta(minutes=expires_min)
        dump = to_encode.model_dump(exclude_unset=True)

        encode_jwt = jwt.encode(
            dump, key=settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
        )
        return encode_jwt


class TokenData(BaseModel):
    access_token: str = Field(description="访问令牌")
    refresh_token: str = Field(description="刷新令牌")
    token_type: str = "bearer"

    @classmethod
    def create(
        cls,
        payload: Payload,
        expires_min: int | None = None,
        refresh_expires: int | None = None,
        token_type: str = "bearer",
    ) -> Self:
        """
        原始Token创建

        Args:
            payload (Payload): 负载
            expires_min (int, optional): 有效期. Defaults to 15.
            refresh_expires (int, optional): 刷新令牌有效期. Defaults to 43200.
            token_type (str, optional): 令牌类型. Defaults to "bearer".

        Returns:
            Self: 令牌数据
        """
        settings = BaseSettings()
        expires_min = expires_min or settings.JWT_EXPIRE_MINUTES
        refresh_expires = refresh_expires or settings.JWT_REFRESH_EXPIRE_MINUTES

        access_token_pl = payload.model_copy()
        refresh_token_pl = payload.model_copy()

        # XXX: 这里有个问题，我认为应该启用Scope。
        # refresh_token应该限制只能访问刷新令牌接口，其他接口禁止访问。

        # XXX: OpenAPI的Oauth2AuthorizationCodeBeaerer模式无法传递Scope表单，导致了通过
        # OpenAPI来创建Token是无法

        access_token = access_token_pl.to_jwt(expires_min)
        refresh_token = refresh_token_pl.to_jwt(refresh_expires)
        return cls(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=token_type,
        )


access_token_bearer = HTTPBearer(scheme_name="Access Token", description="JWT访问令牌")
AccessTokenADP = Annotated[HTTPAuthorizationCredentials, Depends(access_token_bearer)]


def jwt_token_payload(access_token: AccessTokenADP):
    """
    抽取JWT访问令牌负载的依赖项

    这个依赖项主要用于解析出访问令牌的负载。

    Args:
        access_token (AccessTokenADP): 访问令牌

    Raises:
        JWTUnauthorizedError: 未认证异常

    Returns:
        Payload: 负载
    """

    try:
        payload = Payload.from_jwt(access_token.credentials)
        return payload
    except JWTError as e:
        raise JWTUnauthorizedError(str(e))


# endregion


# region ScopeSecurity


class ScopeBase(enum.StrEnum):
    """Scopes配置基类
    继承这个类，然后在模型内部定义Scope。通过to_scopes_map方法获取Scopes字典。

    设计这个类的目的是为了能够像枚举一样定义Scope，并且兼容类型检查。

    ```
    class MyScopes(ScopesBase):
        user:str = Field(description="用户读写权限")

    map = MyScopes.scope_map
    # {"user":"用户读取权限"}
    ```

    Args:
        BaseModel (_type_): _description_

    Returns:
        _type_: _description_
    """

    @classmethod
    @property
    def scopes_map(cls):
        scopes_map = {}
        for k, v in cls.__members__.items():
            scopes_map[k] = v
        return scopes_map


# XXX: 用ContextVar的方式来全局注册唯一的Scope枚举类，auth模块中的Bearer认证就可以通过
# scope_var来获取一个抽象的Scope枚举。具体的Scope枚举可以别的地方定义，然后register_scope_cls
# 的方式注册进去。
scopes_var = ContextVar[dict[str, str]]("scopes_var", default={})


def register_scope(cls: type[ScopeBase]):
    """
    注册Scope类

    Args:
        cls (type[ScopeBase]): 需要注册的Scope类
    """
    scopes = scopes_var.get()
    maps = cls.scopes_map
    scopes.update(maps)
    scopes_var.set(scopes)


def get_scopes() -> dict[str, str]:
    """
    获取当前注册的scopes

    Returns:
        dict[str, str]: scopes 表
    """
    scopes = scopes_var.get()
    return scopes


class Scope(ScopeBase):
    all = "all"
    refresh_token = "refresh_token"


register_scope(Scope)


def _check_scope(
    security_scopes: SecurityScopes,
    payload: Annotated[Payload, Depends(jwt_token_payload)],
):
    if "all" not in payload.scopes:
        for scope in security_scopes.scopes:
            if scope not in payload.scopes:
                raise JWTUnauthorizedError(
                    detail="Token访问域权限不足", scopes=security_scopes
                )


def CheckScope(*scopes: ScopeBase):
    """wrap Security，scopes参数改成用Scope枚举。

    Args:
        scopes (Sequence[Scope] | None, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """

    array = []
    if scopes:
        array = [scope.name for scope in scopes]

    return Security(_check_scope, scopes=array)


RefreshTokenScope = CheckScope(Scope.refresh_token)

# endregion
