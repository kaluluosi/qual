from qual.core.xyapi.database.sqlalchemy_activerecord import Model
from qual.apps.user.model import User


def seed_user():
    if User.get_by_username("admin") is None:
        admin = User(username="admin", display_name="admin")
        admin.set_password("admin")
        admin.save()


def seed():
    with Model.start_session(True):
        seed_user()
