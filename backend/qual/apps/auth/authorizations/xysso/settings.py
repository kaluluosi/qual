from qual.core.xyapi.settings import BaseSettings


class Settings(BaseSettings):
    """
    认证相关配置.
    """

    XYSSO_CLIENT_ID: str = ""
    XYSSO_CLIENT_SECRET: str = ""
    XYSSO_AUTHORIZE_ENDPOINT: str = ""
    XYSSO_TOKEN_ENDPOINT: str = ""
    XYSSO_PROFILE_ENDPOINT: str = ""
