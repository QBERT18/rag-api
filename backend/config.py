from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

_ENV_FILE = Path(__file__).parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    cors_allow_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]

    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "gemma3:1b"
    ollama_embedding_model: str = "nomic-embed-text"

    chroma_db_path: str = "./chroma_db"

    workspace_db_path: str = "./workspace.db"
    context_history_messages: int = 8

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def _split_csv(cls, v):
        if isinstance(v, str) and not v.strip().startswith("["):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v


settings = Settings()
