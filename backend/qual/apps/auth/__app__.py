from qual.core.xyapi import installer, FastAPI
from .router import api
from starlette.middleware.sessions import SessionMiddleware


@installer(__name__)
def install(app: FastAPI):
    # 安装控制器
    app.include_router(api)
    app.add_middleware(
        SessionMiddleware, secret_key="secret", session_cookie="session_id"
    )


def initializer():
    ...
