import apps  # noqa: F401
import qual.contrib.xyapi as xyapi
from fastapi import FastAPI
from uvicorn import run


app = FastAPI()
xyapi.init(app)


def serve():
    run(app)