import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

_client = chromadb.PersistentClient(path="./chroma_db")

_ef = OllamaEmbeddingFunction(
    model_name="nomic-embed-text",
    url="http://localhost:11434",
)

collection = _client.get_or_create_collection(
    name="personal_profile",
    embedding_function=_ef,
)


def reset_collection() -> int:
    ids = collection.get()["ids"]
    if ids:
        collection.delete(ids=ids)
    return len(ids)
