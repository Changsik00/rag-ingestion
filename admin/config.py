from pydantic_settings import BaseSettings, SettingsConfigDict


class AdminConfig(BaseSettings):
    api_url: str = "http://localhost:8000/api/v1/admin"

    model_config = SettingsConfigDict(env_prefix="ADMIN_", env_file=".env", env_file_encoding="utf-8", extra="ignore")
