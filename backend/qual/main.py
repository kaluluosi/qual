import qual.apps
from qual.core import xyapi
from fastapi import FastAPI
from qual.core.settings import settings

app = FastAPI(debug=settings.DEBUG)


xyapi.init(app, qual)
