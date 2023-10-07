import logging
from uvicorn import run
from qual.core.settings import settings


logger = logging.getLogger(__name__)


def serve():
    reload = settings.ENVIRONMENT == "dev"
    run("qual.main:app", reload=reload, host=settings.HOST, port=settings.PORT)


logger.debug("qual模块导入")
