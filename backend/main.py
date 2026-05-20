import json
from collections import Counter

import chat_store
import ollama
from config import settings
from db import collection, reset_collection
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from parsers import get_parser
from prompts import CONTEXT_TEMPLATE, SYSTEM_PROMPT
from pydantic import BaseModel
from retrieval import retrieve

_ollama_client = ollama.Client(host=settings.ollama_base_url)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatCreate(BaseModel):
    title: str | None = None


class ChatRename(BaseModel):
    title: str


def _build_sources(docs: list[str], metas: list[dict]) -> list[dict]:
    return [
        {
            "filename": m.get("source", "?"),
            "line_start": m.get("line_start"),
            "line_end": m.get("line_end"),
            "excerpt": (d[:280] + "…") if len(d) > 280 else d,
        }
        for d, m in zip(docs, metas)
    ]


def _build_chat_messages(history: list[dict], augmented_user: str) -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": augmented_user},
    ]


@app.post("/chats")
def create_chat(body: ChatCreate):
    title = (body.title or "New chat").strip() or "New chat"
    return chat_store.create_chat(title)


@app.get("/chats")
def list_chats():
    return chat_store.list_chats()


@app.patch("/chats/{chat_id}")
def rename_chat(chat_id: int, body: ChatRename):
    title = body.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title cannot be empty")
    chat = chat_store.rename_chat(chat_id, title)
    if not chat:
        raise HTTPException(status_code=404, detail="chat not found")
    return chat


@app.delete("/chats/{chat_id}")
def delete_chat(chat_id: int):
    if not chat_store.delete_chat(chat_id):
        raise HTTPException(status_code=404, detail="chat not found")
    return {"deleted": True}


@app.get("/chats/{chat_id}/messages")
def list_chat_messages(chat_id: int):
    if not chat_store.get_chat(chat_id):
        raise HTTPException(status_code=404, detail="chat not found")
    return chat_store.list_messages(chat_id)


@app.get("/ask/{chat_id}")
def ask(chat_id: int, question: str):
    if not chat_store.get_chat(chat_id):
        raise HTTPException(status_code=404, detail="chat not found")

    history = chat_store.recent_messages_for_context(
        chat_id, settings.chat_history_messages
    )
    chat_store.add_message(chat_id, "user", question)

    docs, metas = retrieve(question)
    context = "\n\n".join(docs)
    augmented_user = CONTEXT_TEMPLATE.format(context=context, question=question)

    response = _ollama_client.chat(
        model=settings.ollama_chat_model,
        messages=_build_chat_messages(history, augmented_user),
    )
    answer = response["message"]["content"]
    sources = _build_sources(docs, metas)
    saved = chat_store.add_message(chat_id, "assistant", answer, sources=sources)

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "message_id": saved["id"],
    }


@app.get("/ask/{chat_id}/stream")
def ask_stream(chat_id: int, question: str):
    if not chat_store.get_chat(chat_id):
        raise HTTPException(status_code=404, detail="chat not found")

    history = chat_store.recent_messages_for_context(
        chat_id, settings.chat_history_messages
    )
    chat_store.add_message(chat_id, "user", question)

    docs, metas = retrieve(question)
    context = "\n\n".join(docs)
    augmented_user = CONTEXT_TEMPLATE.format(context=context, question=question)
    sources = _build_sources(docs, metas)

    def stream():
        full_text = ""
        try:
            yield json.dumps({"type": "sources", "items": sources}) + "\n"
            for chunk in _ollama_client.chat(
                model=settings.ollama_chat_model,
                messages=_build_chat_messages(history, augmented_user),
                stream=True,
            ):
                piece = chunk["message"]["content"]
                full_text += piece
                yield json.dumps({"type": "token", "text": piece}) + "\n"
        finally:
            saved = chat_store.add_message(
                chat_id, "assistant", full_text, sources=sources
            )
            yield json.dumps({"type": "done", "message_id": saved["id"]}) + "\n"

    return StreamingResponse(stream(), media_type="application/x-ndjson")


@app.post("/documents")
async def upload_document(file: UploadFile):
    try:
        parser = get_parser(file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    raw = await file.read()
    chunks = parser.process(raw)
    if not chunks:
        raise HTTPException(status_code=400, detail="No content after parsing")

    collection.add(
        ids=[f"{file.filename}::chunk{i}" for i in range(len(chunks))],
        documents=[c["text"] for c in chunks],
        metadatas=[
            {
                "source": file.filename,
                "chunk_index": i,
                "line_start": c["line_start"],
                "line_end": c["line_end"],
            }
            for i, c in enumerate(chunks)
        ],
    )
    return {"filename": file.filename, "chunks_added": len(chunks)}


@app.get("/documents")
def list_documents():
    data = collection.get()
    counts = Counter(m["source"] for m in data["metadatas"])
    return [{"filename": name, "chunks_count": n} for name, n in sorted(counts.items())]


@app.delete("/documents")
def delete_all_documents():
    deleted = reset_collection()
    return {"deleted_chunks": deleted}


@app.delete("/documents/{filename}")
def delete_document(filename: str):
    data = collection.get(where={"source": filename})
    ids = data["ids"]
    if not ids:
        raise HTTPException(status_code=404, detail="No such document")
    collection.delete(ids=ids)
    return {"deleted_chunks": len(ids)}
