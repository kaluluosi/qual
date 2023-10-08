from fastapi import FastAPI
from qual.core.xyapi import installer
from .authorizations.xysso import router as sso
from .authorizations.oauth2password import router as oauth2password
from .router import api


@installer(__name__)
def install(app: FastAPI):
    # 安装sso登录接口
    app.include_router(sso.api)
    app.include_router(oauth2password.api)
    app.include_router(api)
