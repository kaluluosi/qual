import logging
from qual.core.settings import settings
from sqlalchemy import create_engine
from qual.core.xyapi.database.sqlalchemy_activerecord import Model


logger = logging.getLogger(__name__)

engine = create_engine(settings.DB_DSN, echo=settings.DEBUG)
Model.bind(engine)
