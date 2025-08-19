from pydantic import HttpUrl, SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.sample", env_file_encoding="utf-8")

    api_url: HttpUrl = ""
    api_token: SecretStr = "" # bearer token
    sqlite_db: str = ":memory:"
    buffer_size: int = Field(default=10000, ge=1, lt=100000) # arbitrary buffer size
    max_page_size: int = Field(default=1000, ge=1)

cli_settings = Settings()
