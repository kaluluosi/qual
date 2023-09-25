from fastapi import FastAPI
from qual.core.xyapi import installer
from .router import api


@installer(__name__)
def install(app: FastAPI):
    app.include_router(api)
