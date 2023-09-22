from fastapi import APIRouter, status
from qual.apps.user.dao import UserDAO_ADP
from qual.apps.user.schema import UserRead, UserCreate
from qual.core.xyapi import AccessTokenPayloadADP, ExistedError

api = APIRouter(prefix="/user", tags=["user"])


@api.get("/me", response_model=UserRead)
async def current_user(payload: AccessTokenPayloadADP, user_dao: UserDAO_ADP):
    user = user_dao.get_by_username(payload.sub)
    return user


@api.post("", status_code=status.HTTP_201_CREATED)
async def sign_in(user_c: UserCreate, user_dao: UserDAO_ADP):
    """
    注册用户

    TODO: 有个严重的问题，这个注册接口是无需权限的，那么就要防止恶意请求。
    XXX: 怎么限流？ 认证码？
    """
    user = user_dao.get_by_username(user_c.username)
    if user:
        raise ExistedError(detail=f"用户名 {user_c.username} 已经存在")

    user_dao.create(user_c)
