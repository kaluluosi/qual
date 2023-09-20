import base64
from urllib.parse import urlencode
from fastapi.security import OAuth2AuthorizationCodeBearer
import httpx
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from qual.core.xyapi.security import (
    TokenData,
    Payload,
    get_scopes,
    RefreshTokenScope,
    CheckScope,
)
from .settings import Settings as AuthSettings
from .schema import XYTokenResponse, OAuth2AuthorizationCodeForm

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
        _type_: _description_
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


@api.get("")
async def get_sso_url(redirect_uri: str):
    """
    这个接口是给前端用的。

    流程（vue为例子）：
    1. 前端将自己的登录页url作为 `redirect_uri` 参数发送到这个接口
    2. 这个接口生成一个 xysso 单点登录页面链接，当认证成功后会重定向到 `redirect_uri`
    3. 当sso页面登录成功后重定向到`redirect_uri`并带上 `code` `xycode` 两个查询参数。
    4. 前端 `redirect_uri` 页面拿到授权码后再通过 `/xysso/token` 接口获取 `access token` `refresh token`。
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
    return sso_url


@api.post("/token", response_model=TokenData)
async def sso_token(
    request: Request, form: Annotated[OAuth2AuthorizationCodeForm, Depends()]
):
    """
    这个接口有两个作用：

    1. 给OpenAPI的 `oauth2_redirect` 页面去获取 `access_token`
    2. 给前端调用获取 `access_token`（通过提交表单将`code`发送过来）

    Args:
        request (Request): _description_
        form (Annotated[OAuth2AuthorizationCodeForm, Depends): _description_

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
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
    # 有就直接读取数据库的用户创建Token。 这一步是可以封装成通用的。
    token = TokenData.create(Payload(sub=xy_resp.username))
    return token


xysso_bearer = OAuth2AuthorizationCodeBearer(
    authorizationUrl=auth_settings.XYSSO_AUTHORIZE_ENDPOINT,
    tokenUrl=api.url_path_for("sso_token"),
    # refreshUrl=api.url_path_for("sso_refresh_token"), # OpenAPI的token刷新完全是废的，所以设置了
    scheme_name="XYSSO-心源单点登录",
    description="前端单点登录看`/xysso`接口说明",
    scopes=get_scopes(),
    auto_error=True,  # 认证无效的时候自动抛出 HttpException
)
