from typing import Annotated
from fastapi import APIRouter, Body, HTTPException, status
from qual.apps.user.constant import AccountType
from qual.apps.user.dao import UserDAO_ADP
from qual.apps.user.schema import UserRead, UserCreate, UserUpdate
from qual.core.xyapi import AccessTokenPayloadADP, ExistedError
from qual.core.xyapi.exception import NotFoundError
from qual.core.xyapi.security import verify_password

api = APIRouter(prefix="/user", tags=["user"])


@api.get("/me", response_model=UserRead)
async def current_user(payload: AccessTokenPayloadADP, user_dao: UserDAO_ADP):
    user = user_dao.get_by_username(payload.sub)
    return user


@api.patch("/me", response_model=UserRead)
async def update_current_user(
    user_u: UserUpdate, payload: AccessTokenPayloadADP, user_dao: UserDAO_ADP
):
    user = user_dao.get_by_username(payload.sub)
    update_data = user_u.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(user, k, v)

    return user


@api.patch("/me/password")
async def reset_password(
    password: Annotated[str, Body()],
    payload: AccessTokenPayloadADP,
    user_dao: UserDAO_ADP,
):
    """
    重置密码

    Args:
        password (Annotated[str, Body): 密码

    Raises:
        HTTPException: 密码冲突
        NotFoundError: 用户无效
    """
    user = user_dao.get_by_username(payload.sub)
    if user:
        if verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="新密码与旧密码一样"
            )

        user_dao.update_password(user, password)
    else:
        raise NotFoundError(detail="用户不存在")


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
    user_c.account_type = AccountType.local
    user_dao.create(user_c)


@api.get("", response_model=list[UserRead])
async def get_users(payload: AccessTokenPayloadADP, user_dao: UserDAO_ADP):
    return user_dao.get()


@api.get("/{id}", response_model=UserRead)
async def get_user(id: int, user_dao: UserDAO_ADP):
    user = user_dao.get_by_id(id)
    if not user:
        raise NotFoundError(detail=f"用户 {id} 不存在")

    return user
