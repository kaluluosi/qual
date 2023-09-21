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
from .settings import BaseSettings

settings = BaseSettings()

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
        payload = jwt.decode(
            token, key=settings.JWT_SECRET, algorithms=settings.JWT_ALGORITHM
        )
        payload = cls.model_validate(payload)
        return payload

    def to_jwt(self, expires_min: int = 15) -> str:
        """
        将payload加密成Token串

        Args:
            payload (Self): 负载
            expires_min (int, optional): 有效期（分钟），会用来生成`utcnow+expires_min`的时间戳给exp. Defaults to 15.

        Returns:
            str: token str
        """

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
        expires_min: int = settings.JWT_EXPIRE_MINUTES,
        refresh_expires: int = settings.JWT_REFRESH_EXPIRE_MINUTES,
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
        expires_min = expires_min
        refresh_expires = refresh_expires

        access_token_pl = payload.model_copy()
        refresh_token_pl = payload.model_copy()
        refresh_token_pl.scopes.append(
            Scope.refresh_token
        )  # 限制refresh_token只能用于refresh_token Scope的接口

        # XXX: 这里有个问题，我认为应该启用Scope。
        # refresh_token应该限制只能访问刷新令牌接口，其他接口禁止访问。

        # XXX: OpenAPI的Oauth2AuthorizationCodeBeaerer模式无法传递Scope表单，导致了通过
        # OpenAPI来创建Token是没有Scope的

        access_token = access_token_pl.to_jwt(expires_min)
        refresh_token = refresh_token_pl.to_jwt(refresh_expires)
        return cls(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=token_type,
        )

    @classmethod
    def simple_create(
        cls,
        username: str,
        scopes: list[str],
        expires_min: int = settings.JWT_EXPIRE_MINUTES,
        refresh_expires: int = settings.JWT_REFRESH_EXPIRE_MINUTES,
        token_type: str = "bearer",
    ):
        """
        这是个简易jwt创建接口，通过username和scopes创建令牌。

        Args:
            username (str): _description_
            scopes (list[str]): _description_
            expires_min (int, optional): _description_. Defaults to settings.JWT_EXPIRE_MINUTES.
            refresh_expires (int, optional): _description_. Defaults to settings.JWT_REFRESH_EXPIRE_MINUTES.
            token_type (str, optional): _description_. Defaults to "bearer".

        Returns:
            _type_: _description_
        """
        access_token_payload = Payload(sub=username, scopes=scopes)
        refresh_token_payload = access_token_payload.model_copy()
        refresh_token_payload.scopes = [
            Scope.refresh_token
        ]  # 限制refresh_token只能用于refresh_token Scope的接口

        access_token = access_token_payload.to_jwt(expires_min)
        refresh_token = refresh_token_payload.to_jwt(refresh_expires)

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


class ScopeMeta(type):
    __scopes__: dict[str, str] = {}

    def __setattr__(self, __name: str, __value: Any) -> None:
        self.__scopes__[__name] = __value

    def __getattr__(self, item: str) -> str:
        if item not in self.__scopes__:
            self.__scopes__[item] = item

        return self.__scopes__[item]

    @property
    def scopes(cls):
        return cls.__scopes__


class Scope(metaclass=ScopeMeta):
    """
    Scope定义搜集器

    用法：
    ```python
    # 你只需要像访问成员变量一样
    Scope.user_read

    # 那么Scope 内部就会产生一个记录
    {
        'user_read':'user_read'
    }

    # 如果你想要描述，就给变量赋值字符串
    # 这个中文描述会显示在 OpenAPI认证工具的Scopes参数中。
    Scope.user_read = "用户:读取"

    # 通过 Scope.scopes 可以获取到这个 Scope Map。
    xysso_bearer = OAuth2AuthorizationCodeBearer(
        authorizationUrl=auth_settings.XYSSO_AUTHORIZE_ENDPOINT,
        tokenUrl=api.url_path_for("sso_token"),
        scheme_name="XYSSO-心源单点登录",
        scopes=Scope.scopes, # <- 你可以将这个scopes 复制给 OAuth2的Security基类的scopes参数
    )

    # 这样 OpenAPI页面的认证工具就可以读取到Scope。

    ```

    """

    ...


# 预定义Scope
Scope.all = "全范围权限"
Scope.refresh_token = "刷新令牌"

# endregion
