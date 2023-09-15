from uvicorn import run
from qual.core.settings import settings


def serve():
    reload = settings.ENVIRONMENT == "dev"
    run("qual.main:app", reload=reload, host=settings.HOST, port=settings.PORT)
