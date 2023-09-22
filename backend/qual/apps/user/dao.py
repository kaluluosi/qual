from fastapi import Depends
from sqlalchemy import select
from qual.core.xyapi.database.sqlalchemy import SessionADP
from qual.core.xyapi.security import hash_password
from typing import Annotated
from .model import User
from .schema import UserCreate, UserUpdate


class DAO:
    def __init__(self, session: SessionADP) -> None:
        """
        DOA是一个依赖项，`session` 是作为依赖在控制器里传入。当控制器执行结束的时候
        `session`会自动`commit`。

        缺点是这是个依赖项，无法独立与请求执行。

        Args:
            session (AsyncSessionADP): 会话依赖项
        """
        self.session = session

    def get_by_id(self, id: int):
        user = self.session.get(User, id)
        return user

    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        user = self.session.scalar(stmt)
        return user

    def get(self, offset: int | None = None, limit: int | None = None):
        """
        获取所有用户。

        TODO: 不知道分页要怎么实现，之后再去参考 `fastapi-pagination`

        返回的是个 `ScalarResult` 生成器，避免一次过都加载进内存。

        Returns:
            Coroutine[Any, Any, ScalarResult[_T@scalars]]: 生成器
        """
        stmt = select(User).offset(offset).limit(limit)
        return self.session.scalars(stmt)

    def create(self, user_c: UserCreate) -> User:
        if user_c.password:
            user_c.password = hash_password(user_c.password)
        user = User(**user_c.model_dump())
        self.session.add(user)
        self.session.flush()
        return user

    def update_password(self, user: User, password: str):
        user.password = hash_password(password)

    def update(self, user: User, user_u: UserUpdate):
        update_data = user_u.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(user, k, v)


UserDAO_ADP = Annotated[DAO, Depends(DAO)]
