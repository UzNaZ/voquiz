from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL
import pydantic_core


class Settings(BaseSettings):
    API_PREFIX: str = "/api"


settings = Settings()
