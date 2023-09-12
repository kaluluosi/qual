from qual.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


engine = create_engine(settings.DB_DSN)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    ...
