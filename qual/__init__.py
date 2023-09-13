import qual.apps  # noqa: F401
import qual.core.xyapi as xyapi
from fastapi import FastAPI
from uvicorn import run
from qual.core.config import settings, Environment


app = FastAPI(debug=settings.DEBUG)
xyapi.init(app)


def serve():
    reload = settings.ENVIROMENT == Environment.development
    run("qual:app", reload=reload, host=settings.HOST, port=settings.PORT)
