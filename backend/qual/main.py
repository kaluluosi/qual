import qual.apps
from qual.core import xyapi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from qual.core.settings import settings


app = FastAPI(debug=settings.DEBUG)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
xyapi.init(app, qual)
