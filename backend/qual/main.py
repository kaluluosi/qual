"""
这个模块只负责创建和组装app，不运行。

"""

import qual
from qual.core import xyapi
from qual.core.database import BaseModel
from qual.core.settings import settings
from sqlalchemy import create_engine
from fastapi import FastAPI

app = FastAPI(debug=settings.DEBUG)
xyapi.init(app, qual)


@app.on_event("startup")
def _on_start():
    engine = create_engine(settings.DB_DSN, echo=settings.DEBUG)
    BaseModel.bind(engine)
