from fastapi import FastAPI
from qual.core.xyapi import installer
from .authorizations.xysso import router as sso
from .router import api


@installer(__name__)
def install(app: FastAPI):
    # 安装sso登录接口
    api.include_router(sso.api)
    app.include_router(api)
