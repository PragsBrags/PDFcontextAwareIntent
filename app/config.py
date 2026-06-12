from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    qdrant_url: str
    qdrant_collection: str = "document_chunks"
    embedding_model: str = "embeddinggemma"
    chat_model: str = "llama3.1"
    enabled:str = "True"
    create_tables:str = "True"

    class Config:
        env_file = ".env"


settings = Settings()