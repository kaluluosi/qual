import qual.apps
from qual.core import xyapi
from fastapi import FastAPI
from uvicorn import run
from qual.core.config import settings, Environment

app = FastAPI(debug=settings.DEBUG)
xyapi.init(app, qual)


def serve():
    reload = settings.ENVIRONMENT == Environment.development
    run("qual:app", reload=reload, host=settings.HOST, port=settings.PORT)
