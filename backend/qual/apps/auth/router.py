from fastapi import APIRouter
from qual.core.xyapi.database.sqlalchemy import SessionADP

api = APIRouter(prefix="/auth", tags=["Auth"])


@api.get("/test")
async def test(session: SessionADP):
    ...
