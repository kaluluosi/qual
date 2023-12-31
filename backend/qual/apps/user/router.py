from typing import Annotated
from fastapi import APIRouter, Body, HTTPException, status
from qual.core.xyapi import ExistedError
from qual.core.xyapi.exception import NotFoundError
from qual.core.xyapi.security import verify_password
from qual.core.authentication import AuthenticateADP
from .schema import UserRead, UserCreate, UserUpdate
from .model import User, AccountType

api = APIRouter(prefix="/user", tags=["user"])


@api.get("/me", response_model=UserRead)
async def current_user(me: AuthenticateADP):
    return me


@api.patch("/me", response_model=UserRead)
async def update_current_user(user_u: UserUpdate, me: AuthenticateADP):
    me.update(**user_u.model_dump())


@api.patch("/me/password")
async def reset_password(
    password: Annotated[str, Body()],
    me: AuthenticateADP,
):
    """
    重置密码

    Args:
        password (Annotated[str, Body): 密码

    Raises:
        HTTPException: 密码冲突
        NotFoundError: 用户无效
    """
    if me:
        if verify_password(password, me.password):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="新密码与旧密码一样"
            )
        me.set_password(password)
        me.save()
    else:
        raise NotFoundError(detail="用户不存在")


@api.get("", response_model=list[UserRead])
async def get_users(_me: AuthenticateADP):
    return User.scalars(User.select.where()).all()


@api.get("/{id}", response_model=UserRead)
async def get_user(id: int, _me: AuthenticateADP):
    user = User.get_by_pk(id)
    if not user:
        raise NotFoundError(detail=f"用户 {id} 不存在")

    return user


@api.post("", status_code=status.HTTP_201_CREATED)
async def sign_in(user_c: UserCreate):
    """
    注册用户

    TODO: 有个严重的问题，这个注册接口是无需权限的，那么就要防止恶意请求。
    XXX: 怎么限流？ 认证码？
    """
    user = User.get_by_username(user_c.username)
    if user:
        raise ExistedError(detail=f"用户名 {user_c.username} 已经存在")
    user_c.account_type = AccountType.local
    user = User(**user_c.model_dump())
    user.set_password(user_c.password)
    user.save()
