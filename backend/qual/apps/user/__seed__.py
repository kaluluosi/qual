from .dao import DAO
from .schema import UserCreate
from qual.core.xyapi.database.sqlalchemy import create_session

with create_session() as session:
    dao = DAO(session)

    dao.first_or_create(
        UserCreate(username="admin", display_name="admin", password="admin")
    )
