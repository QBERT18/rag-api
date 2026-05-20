import json
from collections import Counter

import ollama
import workspace_store
from config import settings
from db import clear_collection, drop_collection, get_collection
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


class WorkspaceCreate(BaseModel):
    name: str


class WorkspaceRename(BaseModel):
    name: str


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


def _require_workspace(workspace_id: str) -> dict:
    ws = workspace_store.get_workspace(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="workspace not found")
    return ws


@app.post("/workspaces")
def create_workspace(body: WorkspaceCreate):
    name = body.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="name cannot be empty")
    return workspace_store.create_workspace(name)


@app.get("/workspaces")
def list_workspaces():
    return workspace_store.list_workspaces()


@app.get("/workspaces/{workspace_id}")
def get_workspace(workspace_id: str):
    return _require_workspace(workspace_id)


@app.patch("/workspaces/{workspace_id}")
def rename_workspace(workspace_id: str, body: WorkspaceRename):
    name = body.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="name cannot be empty")
    ws = workspace_store.rename_workspace(workspace_id, name)
    if not ws:
        raise HTTPException(status_code=404, detail="workspace not found")
    return ws


@app.delete("/workspaces/{workspace_id}")
def delete_workspace(workspace_id: str):
    if not workspace_store.delete_workspace(workspace_id):
        raise HTTPException(status_code=404, detail="workspace not found")
    drop_collection(workspace_id)
    return {"deleted": True}


@app.get("/workspaces/{workspace_id}/messages")
def list_workspace_messages(workspace_id: str):
    _require_workspace(workspace_id)
    return workspace_store.list_messages(workspace_id)


@app.get("/ask/{workspace_id}")
def ask(workspace_id: str, question: str):
    _require_workspace(workspace_id)

    history = workspace_store.recent_messages_for_context(
        workspace_id, settings.context_history_messages
    )
    workspace_store.add_message(workspace_id, "user", question)

    docs, metas = retrieve(workspace_id, question)
    context = "\n\n".join(docs)
    augmented_user = CONTEXT_TEMPLATE.format(context=context, question=question)

    response = _ollama_client.chat(
        model=settings.ollama_chat_model,
        messages=_build_chat_messages(history, augmented_user),
    )
    answer = response["message"]["content"]
    sources = _build_sources(docs, metas)
    saved = workspace_store.add_message(
        workspace_id, "assistant", answer, sources=sources
    )

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "message_id": saved["id"],
    }


@app.get("/ask/{workspace_id}/stream")
def ask_stream(workspace_id: str, question: str):
    _require_workspace(workspace_id)

    history = workspace_store.recent_messages_for_context(
        workspace_id, settings.context_history_messages
    )
    workspace_store.add_message(workspace_id, "user", question)

    docs, metas = retrieve(workspace_id, question)
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
            saved = workspace_store.add_message(
                workspace_id, "assistant", full_text, sources=sources
            )
            yield json.dumps({"type": "done", "message_id": saved["id"]}) + "\n"

    return StreamingResponse(stream(), media_type="application/x-ndjson")


@app.post("/workspaces/{workspace_id}/documents")
async def upload_document(workspace_id: str, file: UploadFile):
    _require_workspace(workspace_id)
    try:
        parser = get_parser(file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    raw = await file.read()
    chunks = parser.process(raw)
    if not chunks:
        raise HTTPException(status_code=400, detail="No content after parsing")

    get_collection(workspace_id).add(
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


@app.get("/workspaces/{workspace_id}/documents")
def list_documents(workspace_id: str):
    _require_workspace(workspace_id)
    data = get_collection(workspace_id).get()
    counts = Counter(m["source"] for m in data["metadatas"])
    return [{"filename": name, "chunks_count": n} for name, n in sorted(counts.items())]


@app.delete("/workspaces/{workspace_id}/documents")
def delete_all_documents(workspace_id: str):
    _require_workspace(workspace_id)
    deleted = clear_collection(workspace_id)
    return {"deleted_chunks": deleted}


@app.delete("/workspaces/{workspace_id}/documents/{filename}")
def delete_document(workspace_id: str, filename: str):
    _require_workspace(workspace_id)
    col = get_collection(workspace_id)
    data = col.get(where={"source": filename})
    ids = data["ids"]
    if not ids:
        raise HTTPException(status_code=404, detail="No such document")
    col.delete(ids=ids)
    return {"deleted_chunks": len(ids)}
