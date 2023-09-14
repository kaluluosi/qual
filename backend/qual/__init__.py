import qual.apps
from qual.core import xyapi
from fastapi import FastAPI
from uvicorn import run
from qual.core.settings import settings

app = FastAPI(debug=settings.DEBUG)
xyapi.init(app, qual)


def serve():
    reload = settings.ENVIRONMENT == "dev"
    run("qual:app", reload=reload, host=settings.HOST, port=settings.PORT)
