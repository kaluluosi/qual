import base64
import httpx
import logging
from urllib.parse import urlencode
from fastapi.security import OAuth2AuthorizationCodeBearer
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from qual.core.xyapi.security import NeedScope, TokenData, Scope, Payload
from .settings import Settings as AuthSettings
from .schema import XYTokenResponse, OAuth2AuthorizationCodeForm, XYSSOInfo
from qual.core.xyapi.security import AccessTokenADP

logger = logging.getLogger(__name__)

api = APIRouter(prefix="/xysso", tags=["xysso"])
auth_settings = AuthSettings()


async def req_xyuserinfo(code: str, client_id: str, client_secret: str):
    """
    请求xy用户信息。封装的 `XYSSO_TOKEN_ENDPOINT` 的请求。

    Args:

        code (_type_): sso返回的授权码
        client_id (_type_): 客户端id
        client_secret (_type_): 客户端密文

    Returns:

        XYTokenResponse: XYSSO_TOKEN_ENPOINT的响应体
    """

    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(
            auth_settings.XYSSO_TOKEN_ENDPOINT,
            params=dict(
                auth_string=base64.b64encode(
                    f"{client_id}:{client_secret}".encode("utf-8")
                ).decode("utf-8"),
                xycode=code,
            ),
        )

        xy_resp = XYTokenResponse(**response.json())
    return xy_resp


@api.options("")
async def sso_url(redirect_uri: str | None = ""):
    """
    这个接口是给前端用的。

    流程（vue为例子）：
    1. 前端将自己的登录页url作为 `redirect_uri` 参数发送到这个接口
    2. 这个接口生成一个 xysso 单点登录页面链接，当认证成功后会重定向到 `redirect_uri`
    3. 当sso页面登录成功后重定向到`redirect_uri`并带上 `code` `xycode` 两个查询参数（授权码）。
    4. 前端 `redirect_uri` 页面拿到`code`后再通过 `/xysso/token` 接口获取 `access token` `refresh token`。
    5. 将 `access token` 前端保存起来（最好保存在`sessionstorage`)，以后请求的时候 `header` 带上 `Authorization: Bearer <access token>`
    6. 将 `refresh token` 保存在 `localstorage`。

    如果 `access token` 不存在或者请求后得到 `token过期错误`，那么就用刷新token接口来获取新的 `token 组`。

    Args:

        redirect_uri (str): 重定向回去

    Returns:

        str: url
    """

    query_params = urlencode(
        dict(
            client_id=auth_settings.XYSSO_CLIENT_ID,
            response_type="code",
            redirect_uri=redirect_uri,
        )
    )

    sso_url = f"{auth_settings.XYSSO_AUTHORIZE_ENDPOINT}?{query_params}"

    ssoinfo = XYSSOInfo(
        client_id=auth_settings.XYSSO_CLIENT_ID,
        response_type="code",
        url=sso_url,
        scopes=Scope.scopes,
        redirect_uri=redirect_uri,
    )

    return ssoinfo


@api.post("/token", response_model=TokenData)
async def sso_token(form: Annotated[OAuth2AuthorizationCodeForm, Depends()]):
    """
    这个令牌接口是SSO专用的，因为内部还调用了 `XYSSO_TOKEN_ENPOINT` 接口获取用户信息

    这个接口有两个作用：

    1. 给OpenAPI的 `oauth2_redirect` 页面去获取 `access_token`
    2. 给前端调用获取 `access_token`（通过提交表单将`code`发送过来）

    由于 `OpenAPI`的严重流程中用的表单提交，因此不得已接口也只能用表单了。

    Args:

        request (Request): 请求体
        form (Annotated[OAuth2AuthorizationCodeForm, Depends): 表单

    Raises:

        HTTPException: XYSSO配置异常

    Returns:

        TokenData: {"access_token":"xxx","refresh_token":"xxx"} 结构
    """

    if not auth_settings.XYSSO_CLIENT_ID or not auth_settings.XYSSO_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="XYSSO_CLIENT_ID、XYSSO_CLIENT_SECRET没有配置。",
        )

    code = form.code
    client_id = form.client_id or auth_settings.XYSSO_CLIENT_ID
    client_secret = form.client_secret or auth_settings.XYSSO_CLIENT_SECRET

    xy_resp = await req_xyuserinfo(code, client_id, client_secret)

    # TODO: 检查数据库里有没有这个用户，没有就创建用户，

    # XXX: 因为XYSSO的一些不规范实现，导致OpenAPI的Scope没有被传递到`oauth2-redirect`页面，因此`form.scope`是空的。
    # 为了避免`OpenAPI`页面创建的Token没有Scope，默认给他一个 `Scope.all` 全能范围。
    # 如果 `form.scope` 不是空，那么就使用 `form` 的 scope。
    scopes = form.scope if form.scope else [Scope.all]

    # token部分是通用的，都是用户名来做负载
    token = TokenData.simple_create(username=xy_resp.username, scopes=scopes)
    logger.debug(f"发放token {token.model_dump()}")
    return token


@api.get("/refresh_token")
async def refresh_token(payload: Payload = NeedScope()):
    if payload.typ != "refresh":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="发送来的Token 不是刷新令牌"
        )

    # TODO ： 刷新令牌
    ...


_description = f"""
前端单点登录看`/xysso`接口说明

> `OpenAPI`的`Available authorizations`中，下面的 `Scopes` 参数是没有用的。
因为 `XYSSO` 的认证接口重定向的时候没有回传 `scopes`参数，丢失了。但是，我们自己编写前端流程可以将`scopes`表单发送的`/xysso/token` 接口。

当前后端配置:

client_id:  {auth_settings.XYSSO_CLIENT_ID}

client_secret:  {auth_settings.XYSSO_CLIENT_SECRET}
"""

xysso_bearer = OAuth2AuthorizationCodeBearer(
    authorizationUrl=auth_settings.XYSSO_AUTHORIZE_ENDPOINT,
    tokenUrl=api.url_path_for("sso_token"),
    # refreshUrl=api.url_path_for("sso_refresh_token"), # OpenAPI的token刷新完全是废的，所以设置了
    scheme_name="XYSSO-心源单点登录",
    description=_description,
    scopes=Scope.scopes,
    auto_error=True,  # 认证无效的时候自动抛出 HttpException
)


api.dependencies.append(Depends(xysso_bearer))


@api.get(
    "/test_sso_auth",
    tags=["test"],
    response_model=AccessTokenADP,
    dependencies=[NeedScope(Scope.user)],
)
async def test(access_token: AccessTokenADP):
    """
    用来测试SSO令牌。

    `OpenAPI`的认证工具登录成功后通过这个接口测试是否能够跑通。
    返回 `200-OK` 还有 `Authorization` 凭据。

    Scopes: <no-scope>
    """
    return access_token
