from pydantic_settings import BaseSettings, SettingsConfigDict


class AdminConfig(BaseSettings):
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "password"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
