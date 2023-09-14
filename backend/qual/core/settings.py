from qual.core.xyapi.settings import BaseSettings


class Settings(BaseSettings):
    # 密码hash用
    SECRET_KEY: str = ""

    DB_DSN: str = "sqlite:///.db.sqlite"


settings = Settings()
