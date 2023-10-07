from functools import lru_cache
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings as Base, SettingsConfigDict


class BaseSettings(Base):
    """
    基础 dotenv 配置

    NOTE: 因为这个基类的 `model_config` 是配置了 `extra='allow'` 的，
    所以这个配置是允许 `.env` 文件中存在额外的配置。也就是说 `Settings`
    只会解析和校验它定义过的字段有没有配置和合不合法，而对于 `.env` 配置了别
    的以外的字段他不会理会。那么就可以做到一件以前做不到的事情：将配置分散在。

    例子：

    比如我们有个 `auth` APP模块，这个模块定义了用户和登录认证相关的功能。
    如果它有一些数据需要公开让 `.env` 来配置，按照以往他需要到项目的 `settings.py`
    下去给 `Settings` 类添加新的字段。这样 `auth` 就跟 `settings.py` 是完全依赖了。
    以后也没办法把 `auth` 模块封装成一个独立的 `package` 做成公用模块。

    现在通过直接继承这个 `Settings`，定义你想要公开的字段，在任何模块实例化
    这个类都能够读取到项目的 `.env` 、解析到你公开的字段。

    """

    ENVIRONMENT: str | Literal["dev", "prod"] = Field(default="dev", description="环境")
    DEBUG: bool = Field(default=False, description="调试模式，主要影响日志、FastApi、数据库打印")
    HOST: str = Field(default="127.0.0.1", description="绑定IP")
    PORT: int = Field(default=8000, description="端口")

    # JWT令牌相关
    JWT_SECRET: str = Field(default="jwt_secret", description="密文")
    JWT_ALGORITHM: str = Field(default="HS256", description="算法")
    JWT_EXPIRE_MINUTES: int = Field(default=30, description="令牌有效期")
    JWT_REFRESH_EXPIRE_MINUTES: int = Field(default=43200, description="刷新令牌有效期")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )
