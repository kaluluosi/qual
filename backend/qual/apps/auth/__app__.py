from qual.core.xyapi import installer, FastAPI
from .router import api


@installer(__name__)
def install(app: FastAPI):
    app.include_router(api)
