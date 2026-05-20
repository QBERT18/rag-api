import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

from config import settings

_client = chromadb.PersistentClient(path=settings.chroma_db_path)

_ef = OllamaEmbeddingFunction(
    model_name=settings.ollama_embedding_model,
    url=settings.ollama_base_url,
)


def collection_name(workspace_id: str) -> str:
    return f"ws_{workspace_id}"


def get_collection(workspace_id: str):
    return _client.get_or_create_collection(
        name=collection_name(workspace_id),
        embedding_function=_ef,
    )


def drop_collection(workspace_id: str) -> None:
    try:
        _client.delete_collection(collection_name(workspace_id))
    except Exception:
        pass


def clear_collection(workspace_id: str) -> int:
    col = get_collection(workspace_id)
    ids = col.get()["ids"]
    if ids:
        col.delete(ids=ids)
    return len(ids)
