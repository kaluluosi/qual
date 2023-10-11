"""app user 初始化数据

Revision ID: 5408227f187b
Revises: 
Create Date: 2023-10-11 03:11:32.043466

"""
from typing import Sequence, Union

from alembic import op
from qual.apps.user.model import User
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "5408227f187b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if not User.get_by_username("admin"):
        admin = User(username="admin", display_name="admin")
        admin.set_password("admin")
        admin.save()


def downgrade() -> None:
    admin = User.get_by_username("admin")
    if admin:
        admin.delete()
