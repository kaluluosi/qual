from qual.core.xyapi.settings import BaseSettings


class Settings(BaseSettings):
    """
    认证相关配置.
    """

    XYSSO_CLIENT_ID: str | None = None
    XYSSO_CLIENT_SECRET: str | None = None
    XYSSO_AUTHORIZE_ENDPOINT: str | None = None
    XYSSO_TOKEN_ENDPOINT: str | None = None
    XYSSO_PROFILE_ENDPOINT: str | None = None
