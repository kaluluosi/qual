from fastapi import APIRouter, HTTPException, status
from qual.core.xyapi.security import RefreshTokenPayloadADP, TokenData
from qual.apps.user.dao import UserDAO_ADP

api = APIRouter(prefix="/auth", tags=["auth"])


@api.post("/refresh_token", response_model=TokenData)
async def refresh_token(payload: RefreshTokenPayloadADP, user_dao: UserDAO_ADP):
    """
    刷新令牌接口

    需要将刷新令牌放到 `Authorization: Bearer <refresh_token>` 中传递过来。

    本接口会校验token负载和用户名是否还有效，如果用户有效就返回一个新的 `Access Token`。

    刷新令牌属于`jwt`认证的公告接口，不属于具体的认证流程接口中。
    """
    username = payload.sub

    if not user_dao.is_valid(username):
        # 如果用户无效就返回失败
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户已经无效")

    token_data = TokenData.simple_create(username=username, scopes=payload.scopes)

    return token_data
