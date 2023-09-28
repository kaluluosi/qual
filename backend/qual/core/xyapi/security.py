"""
安全认证相关

AccessToken的创建和解析

"""

from typing import Annotated, Any, Literal, Self
from fastapi import Depends, Form, Security
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    SecurityScopes,
)
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from .exception import JWTUnauthorizedError
from .settings import BaseSettings

settings = BaseSettings()

# region 密码

# XXX: 写死了,以后不知道要不要改为.env配置的
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
    typ: Literal["access", "refresh"] = Field(default="access", description="类型")
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

        access_token的scope通过scopes参数定义。
        refresh_token的scope默认是空。


        Args:
            username (str): _description_
            scopes (list[str]): 这个scope只会用作access_token，不会用于refresh_token
            expires_min (int, optional): _description_. Defaults to settings.JWT_EXPIRE_MINUTES.
            refresh_expires (int, optional): _description_. Defaults to settings.JWT_REFRESH_EXPIRE_MINUTES.
            token_type (str, optional): _description_. Defaults to "bearer".

        Returns:
            _type_: _description_
        """
        access_token_payload = Payload(sub=username, scopes=scopes)
        access_token_payload.typ = "access"

        refresh_token_payload = access_token_payload.model_copy()
        refresh_token_payload.typ = "refresh"

        access_token = access_token_payload.to_jwt(expires_min)
        refresh_token = refresh_token_payload.to_jwt(refresh_expires)

        return cls(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=token_type,
        )


# 这是通用的从请求Headers中解析`Bearer`令牌的依赖项
# 如果你在请求结果中看到了 `Not authenicated` 那么都是这个依赖项拦截的结果
token_bearer = HTTPBearer(scheme_name="Token", description="JWT令牌")
# 这是Annotated包装好的依赖项
TokenADP = Annotated[HTTPAuthorizationCredentials, Depends(token_bearer)]


def _get_access_token_payload(credential: TokenADP):
    """
    解析 Access Token 的Payload。

    1. 会检查是否是`access`类型的Token。

    2. 会检查是否过期。


    Args:
        credential (TokenADP): _description_

    Raises:
        Exception: Token类型不正确异常
        JWTUnauthorizedError: 认证失败异常
    """
    token = credential.credentials
    try:
        payload = Payload.from_jwt(token)
        if payload.typ != "access":
            raise Exception("Token类型不是 `access`")
    except JWTError as e:
        raise JWTUnauthorizedError(str(e))

    return payload


AccessTokenPayloadADP = Annotated[Payload, Depends(_get_access_token_payload)]


async def _get_refresh_access_token_payload(refresh_token: Annotated[str, Form()] = ""):
    """
    解析 Refresh Token 的Payload。

    会检查是否是 `refresh` 类型的Token。

    [参考Postman的刷新令牌规范流程](https://auth0.com/docs/secure/tokens/refresh-tokens/use-refresh-tokens#use-basic-authentication)

    XXX: 研究Postman的OAuth2和刷新令牌功能的时候发现他们是将刷新令牌放到表单里Post到刷新令牌接口，而不是放到认证头里。
    同时，他们还会再认证头里传递 `Basic {base64(<client_id>:<client_secret>)}`。刷新令牌机制要兼容Postman，因此修改。
    同时也解决了OpenAPI的刷新令牌机制不工作问题（大概）。

    Args:
        refresh_token (str,Form()): 从表单中获取refresh_token

    Raises:
        Exception: Token类型不正确异常
        JWTUnauthorizedError: 认证失败异常
    """
    token = refresh_token
    try:
        payload = Payload.from_jwt(token)
        if payload.typ != "refresh":
            raise JWTUnauthorizedError("Token类型不是 `refresh`")
    except JWTError as e:
        raise JWTUnauthorizedError(str(e))

    return payload


RefreshTokenPayloadADP = Annotated[Payload, Depends(_get_refresh_access_token_payload)]

# endregion


# region ScopeSecurity


class ScopeMeta(type):
    __scopes__: dict[str, str] = {}

    def __setattr__(self, __name: str, __value: Any) -> None:
        self.__scopes__[__name] = __value

    def __getattr__(self, item: str) -> str:
        if item not in self.__scopes__:
            self.__scopes__[item] = item

        return item

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


# `FastAPI`的`Security`是继承自`Depends`，他本身就是当作`Depends`的替代品使用
# 用`Security`包裹的依赖项会将 `scopes` 参数添加到依赖池里。


def access_token_payload(
    token_payload: AccessTokenPayloadADP,
    security_scopes: SecurityScopes,
):
    """
    获取access_token的payload，如果有scopes那么就会去检查权限范围是否匹配。



    Args:

        token_payload (AccessTokenPayloadADP): _description_
        security_scopes (SecurityScopes): _description_

    Raises:

        JWTUnauthorizedError: _description_

    Returns:

        _type_: _description_
    """
    if security_scopes.scopes:
        # 如果scopes非空，意味着这个依赖需要检查scopes
        if Scope.all not in token_payload.scopes:
            for scope in security_scopes.scopes:
                if scope not in token_payload.scopes:
                    raise JWTUnauthorizedError(
                        detail="Token的Scope不满足", scopes=security_scopes
                    )
    return token_payload


def NeedScope(*scope_check: str):
    """
    这个依赖项会解析 `jwt_payload` 并检查 `scopes` 是否满足，然后返回`Payload`

    这个依赖项比较特殊，它返回的是 Security对象，其本身就是个Depends对象，因此不需要用Depends包裹。

    有两种用法：

    一种是当作 `jwt`和`payload` 的依赖项用，这时候不用传`scopes`，返回的依赖就是`Payload`对象。

    另一种是当作`Security`用，由于内部实现也是用的 `SecurityScopes`，所以
    多个


    用法：
    ```python

    @api.get("/username")
    async def get_username(payload:Payload=NeedScope()):
        return payload.sub

    @api.get("/me", dependencies=[NeedScope(Scope.me)])
    async def get_me():
        return "This is me"

    ```

    Returns:
        Callable: ...
    """
    return Security(access_token_payload, scopes=scope_check)


# 预定义Scope
Scope.all = "全范围权限"


# endregion
