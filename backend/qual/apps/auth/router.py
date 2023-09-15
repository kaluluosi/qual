from fastapi import APIRouter
from .schema import UserIn, UserOut
from .dao import UserDAO_ADP


api = APIRouter(prefix="/auth", tags=["Auth"])


@api.get("/user/{id}", response_model=UserOut)
async def get(id: int, user_dao: UserDAO_ADP):
    return user_dao.get_by_id(id)


@api.post("/user", response_model=UserOut)
async def create(user_in: UserIn, user_dao: UserDAO_ADP):
    user = user_dao.create(user_in)
    return user
