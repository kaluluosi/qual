import enum
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(enum.StrEnum):
    development = "dev"
    production = "prod"


class Settings(BaseSettings):
    ENVIRONMENT: Environment = Environment.development
    API_PATH: str = "/api/v1"
    DEBUG: bool = True
    # 密码hash用
    SECRET_KEY: str = ""

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    DB_DSN: str = "sqlite:///.db.sqlite"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
