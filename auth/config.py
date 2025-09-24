from pathlib import Path
from typing import ClassVar

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent


class Settings(BaseSettings):
    google_client_id: SecretStr
    google_client_secret: SecretStr
    secret_key: SecretStr
    algorithm: ClassVar[str] = "HS256"

    postgres_user: SecretStr
    postgres_password: SecretStr
    postgres_db: SecretStr
    postgres_host: str
    postgres_port: int

    model_config = SettingsConfigDict(
        # change to env_file=".env"
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    settings = Settings()
    return settings
