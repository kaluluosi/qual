from typing import Annotated
from fastapi import Form
from pydantic import BaseModel


class OAuth2AuthorizationCodeForm:
    """
    Oauth2授权码表单

    这个表单是为了兼容 `openapi` 的授权码流程定义的。

    `openapi` 的授权码流程中会重定向到一个中间页面`oauth2_redirect`,然后在这个页面中将授权码相关数据
    用表单提交到`openai`页面。

    不是用 json，因此不得已要定义这个类。
    """

    def __init__(
        self,
        *,
        code: Annotated[str, Form()],
        grant_type: Annotated[str | None, Form()] = None,
        client_id: Annotated[str | None, Form()] = None,
        client_secret: Annotated[str | None, Form()] = None,
        redirect_uri: Annotated[str | None, Form()] = None,
        scope: Annotated[str, Form()] = ""
    ) -> None:
        self.grant_type = grant_type
        self.code = code
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope.split()


class UserInfo(BaseModel):
    """
    用户信息
    """

    description: list[str]
    telephoneNumber: list[str]
    whenCreated: list[str]
    memberOf: list[str]
    name: list[str]
    primaryGroupID: list[str]
    objectCategory: list[str]
    lastLogonTimestamp: list[str]
    uid: list[str]
    mail: list[str]
    department: list[str]


class XYTokenResponse(BaseModel):
    """
    XYSSO_TOKEN_ENPOINT 返回的数据
    """

    errcode: int
    errmsg: str
    client_id: str
    username: str
    user: dict[str, UserInfo | str]
    admin: list[str]


class XYSSOInfo(BaseModel):
    client_id: str
    response_type: str = "code"
    scopes: dict[str, str]
    redirect_uri: str | None
    url: str
