import enum
from pydantic_settings import BaseSettings


class Enviroment(enum.StrEnum):
    development = "dev"
    production = "prod"

class Settings(BaseSettings):
    enviroment: Enviroment = Enviroment.development
    api_path:str = "/api/v1"
    