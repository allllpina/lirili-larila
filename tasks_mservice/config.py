from pathlib import Path
from typing import ClassVar

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent


class Settings(BaseSettings):
    database_host: str
    database_port: int
    database_name: SecretStr

    frontend_url: str

    jwt_key: SecretStr
    algorithm: ClassVar[str] = "HS256"

    google_ai_api_key: SecretStr
    google_model: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    settings = Settings()
    return settings
