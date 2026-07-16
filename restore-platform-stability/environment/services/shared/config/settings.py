from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class AppSettings(BaseSettings):
    app_name: str = "service"
    environment: str = "development"
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    log_level: str = "INFO"
    service_port: int = 8000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = AppSettings()
