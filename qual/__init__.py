import qual.apps  # noqa: F401 将app中的模块全部导入以此来实现alembic发现model
import qual.core.xyapi as xyapi
from fastapi import FastAPI
from uvicorn import run
from qual.core.config import settings, Environment


app = FastAPI(debug=settings.DEBUG)
xyapi.init(app)


def serve():
    reload = settings.ENVIRONMENT == Environment.development
    run("qual:app", reload=reload, host=settings.HOST, port=settings.PORT)
