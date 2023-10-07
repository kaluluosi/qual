from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from qual.core.xyapi.exception import HttpExceptionModel
from qual.core.xyapi.security import TokenADP, TokenData, verify_password
from qual.apps.user.constant import AccountType
from qual.apps.user.dao import UserDAO_ADP

api = APIRouter(prefix="/oath2password", tags=["oath2password"])


@api.post(
    "/token",
    response_model=TokenData,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": HttpExceptionModel,
            "description": "用户不存在或者密码错误",
        },
        status.HTTP_409_CONFLICT: {
            "model": HttpExceptionModel,
            "description": "同名的别的类型用户已存在",
        },
    },
)
async def token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()], user_dao: UserDAO_ADP
):
    """
    认证并获取token

    Args:

        form (Annotated[OAuth2PasswordRequestForm, Depends): 表单

    Returns:

        TokenData: {"access_token":"xxx","refresh_token":"xxx"} 结构
    """

    # TODO：校验用户名和密码
    # XXX: 目前 form中的 client_id和 client_secret没有使用上。按照OAuth2的规范
    # 服务端应该存有client_id和client_secret用来校验发请求来的客户端的client_id是否合法，是否有权申请令牌。
    # 现在问题是client_id应该写死后端还是存？这个工具本身也不是作为`rest`大后台使用，并不需要像
    # github、google那样搞大OAuth2开放平台。

    # XXX: 这一段代码就是具体的认证流程逻辑已经粘死这里了
    user = user_dao.get_by_username(username=form.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    elif user.account_type != AccountType.local:  # password模式只认local类型账户
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"用户已存在，但是类型是 {user.account_type}。",
        )
    elif not verify_password(form.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="密码不正确")

    token_data = TokenData.simple_create(username=form.username, scopes=form.scopes)
    return token_data


oauth2_password_bearer = OAuth2PasswordBearer(tokenUrl=api.url_path_for("token"))


@api.get(
    "/test_oauth2_password",
    tags=["test"],
    dependencies=[Depends(oauth2_password_bearer)],
)
async def test(token: TokenADP):
    """
    测试OAuth2密码认证
    """
    return token
