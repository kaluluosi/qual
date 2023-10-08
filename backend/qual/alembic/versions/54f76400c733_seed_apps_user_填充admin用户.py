"""seed apps user 填充admin用户

Revision ID: 54f76400c733
Revises: 8da48a3b5e43
Create Date: 2023-10-08 08:56:09.437896

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from qual.apps.user.dao import DAO
from sqlalchemy.orm import Session

from qual.apps.user.schema import UserCreate


# revision identifiers, used by Alembic.
revision: str = "54f76400c733"
down_revision: Union[str, None] = "8da48a3b5e43"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    with Session(bind=conn) as session:
        dao = DAO(session)

        dao.first_or_create(
            UserCreate(username="admin", password="admin", display_name="admin")
        )


def downgrade() -> None:
    conn = op.get_bind()
    with Session(conn) as session:
        dao = DAO(session)
        dao.delete_by_username("admin")
