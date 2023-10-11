import base64
import logging
from typing import Annotated, cast
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer

from qual.apps.user.model import User, AccountType
from qual.apps.user.schema import UserCreate
from qual.core.xyapi.exception import HttpExceptionModel
from qual.core.xyapi.security import Scope, TokenADP, TokenData

from .schema import OAuth2AuthorizationCodeForm, UserInfo, XYSSOInfo, XYTokenResponse
from .settings import Settings as AuthSettings

logger = logging.getLogger(__name__)

api = APIRouter(prefix="/xysso", tags=["xysso"])
auth_settings = AuthSettings()


@api.post(
    "/userinfo",
    response_model=XYTokenResponse,
    responses={status.HTTP_400_BAD_REQUEST: {"model": HttpExceptionModel}},
)
async def req_xyuserinfo(
    code: Annotated[str, Form()],
    client_id: Annotated[str | None, Form()] = None,
    client_secret: Annotated[str | None, Form()] = None,
):
    """
    请求xy用户信息。封装的 `XYSSO_TOKEN_ENDPOINT` 的请求。

    Args:

        code (_type_): sso返回的授权码
        client_id (_type_): 客户端id，为空会使用后端配置的id
        client_secret (_type_): 客户端密文，为空会使用后端配置的secret

    Returns:

        XYTokenResponse: XYSSO_TOKEN_ENPOINT的响应体
    """
    client_id = client_id or auth_settings.XYSSO_CLIENT_ID
    client_secret = client_secret or auth_settings.XYSSO_CLIENT_SECRET

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

        if xy_resp.errcode == -1 or xy_resp.errmsg != "ok":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=xy_resp.errmsg
            )

        return xy_resp


@api.options("", response_model=XYSSOInfo)
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

        XYSSOInfo: sso认证所需的数据参数
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


@api.post(
    "/token",
    response_model=TokenData,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": HttpExceptionModel,
            "description": "可能是后端SSO配置错误",
        }
    },
)
async def token(form: Annotated[OAuth2AuthorizationCodeForm, Depends()]):
    """
    这个令牌接口是直接用授权码获取了Token。

    内部还调用了 `XYSSO_TOKEN_ENPOINT` 接口获取用户信息。


    这个接口有两个作用：

    1. 给OpenAPI的 `oauth2_redirect` 页面去获取 `access_token`
    2. 给前端调用获取 `access_token`（通过提交表单将`code`发送过来，除了scope有用到，其他参数都没用）

    由于 `OpenAPI`的认证流程中用的表单提交，因此不得已接口也只能用表单了。

    Args:

        request (Request): 请求体
        form (Annotated[OAuth2AuthorizationCodeForm, Depends): 表单（client_id和client_secret并没有使用，而是取后端配置的值）

    Raises:

        HTTPException: XYSSO配置异常

    Returns:

        TokenData: {"access_token":"xxx","refresh_token":"xxx"} 结构
    """

    if not auth_settings.XYSSO_CLIENT_ID or not auth_settings.XYSSO_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="XYSSO_CLIENT_ID、XYSSO_CLIENT_SECRET没有配置。",
        )

    code = form.code
    client_id = auth_settings.XYSSO_CLIENT_ID
    client_secret = auth_settings.XYSSO_CLIENT_SECRET

    xy_resp = await req_xyuserinfo(code, client_id, client_secret)

    # TODO: 检查数据库里有没有这个用户，没有就创建用户
    # XXX: 这里不可避免的要跟具体的创建用户耦合。到底要不要后端这个接口一条龙的创建用户呢？
    user = User.get_by_username(xy_resp.username)
    if not user:
        user_info = list(xy_resp.user.values())[0]
        user_info = cast(UserInfo, user_info)

        user = User(
            username=xy_resp.username,
            display_name=user_info.name[0],
            mail=user_info.mail[0],
            account_type=AccountType.xysso,
        )
        user.save()
        logger.info(f"初次创建xysso用户 {user.username}")

    # XXX: 因为XYSSO的一些不规范实现，导致OpenAPI的Scope没有被传递到`oauth2-redirect`页面，因此`form.scope`是空的。
    # 为了避免`OpenAPI`页面创建的Token没有Scope，默认给他一个 `Scope.all` 全能范围。
    # 如果 `form.scope` 不是空，那么就使用 `form` 的 scope。
    scopes = form.scope if form.scope else [Scope.all]

    # token部分是通用的，都是用户名来做负载
    token_data = TokenData.simple_create(username=xy_resp.username, scopes=scopes)
    logger.debug(f"发放token {token_data.model_dump()}")
    return token_data


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
    tokenUrl=api.url_path_for("token"),
    # refreshUrl=api.url_path_for("sso_refresh_token"), # XXX: OpenAPI的token刷新完全是废的，不知道怎么用，注释了
    scheme_name="XYSSO-心源单点登录",
    description=_description,
    scopes=Scope.scopes,
    auto_error=True,  # 认证无效的时候自动抛出 HttpException
)


@api.get(
    "/test_sso_auth",
    tags=["test"],
    response_model=TokenADP,
    dependencies=[Depends(xysso_bearer)],
)
async def test(token: TokenADP):
    """
    用来测试SSO令牌，返回的是令牌凭证。

    `OpenAPI`的认证工具登录成功后通过这个接口测试是否能够跑通。
    返回 `200-OK` 还有 `Authorization` 凭据。

    Scopes: <no-scope>
    """
    return token
