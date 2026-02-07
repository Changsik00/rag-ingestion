from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "RAG Ingestion Service"
    APP_VERSION: str = "0.1.0"
    API_URL: str = "http://localhost:8000"

    # [Spec 060] Stability & Cleanup
    AUTO_CLEANUP_ENABLED: bool = True

    # LLM & Embedding
    GEMINI_API_KEY: str
    GEMINI_MODEL_NAME: str = "gemini-3-flash-preview"
    GEMINI_EMBEDDING_MODEL_NAME: str = "gemini-embedding-001"
    GEMINI_EMBEDDING_DIMENSIONALITY: int = 3072
    FIRECRAWL_API_KEY: str | None = None

    # Chunking Strategy
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # ChromaDB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_BATCH_SIZE: int = 20

    # Postgres
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "checkpoints"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    @property
    def postgres_db_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


def get_settings() -> Settings:
    return Settings()
