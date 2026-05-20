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

collection = _client.get_or_create_collection(
    name=settings.chroma_collection_name,
    embedding_function=_ef,
)


def reset_collection() -> int:
    ids = collection.get()["ids"]
    if ids:
        collection.delete(ids=ids)
    return len(ids)
