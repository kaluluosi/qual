from fastapi import APIRouter, HTTPException, status
from qual.core.xyapi.security import RefreshTokenPayloadADP, TokenData

api = APIRouter(prefix="/auth", tags=["auth"])


@api.get("/refresh_token")
async def refresh_token(payload: RefreshTokenPayloadADP):
    """
    刷新令牌

    需要将刷新令牌放到 `Authorization: Bearer <refresh_token>` 中传递过来。

    然后返回一个新的 `Access Token`
    """
    username = payload.sub
    # TODO:  通过username查询用户检查用户是否有效。因为用户可能随时被锁定、删除、禁用等等导致无效。
    is_valid = True

    # 如果用户无效就返回失败
    if not is_valid:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户已经无效")

    token_data = TokenData.simple_create(username=username, scopes=payload.scopes)

    return token_data.access_token
