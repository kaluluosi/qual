"""
这个模块只负责创建和组装app，不运行。

"""

import qual
from qual.core import xyapi
from qual.core.settings import settings
from fastapi import FastAPI

app = FastAPI(debug=settings.DEBUG)
xyapi.init(app, qual)
