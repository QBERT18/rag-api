import json
from collections import Counter

import ollama
from db import collection, reset_collection
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from parsers import get_parser
from prompts import ASK_PROMPT
from retrieval import retrieve

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ask")
def ask(question: str):
    docs, _metas = retrieve(question)
    context = "\n\n".join(docs)
    augmented_prompt = ASK_PROMPT.format(context=context, question=question)

    response = ollama.chat(
        model="gemma4",
        messages=[{"role": "user", "content": augmented_prompt}],
    )

    return {
        "question": question,
        "answer": response["message"]["content"],
        "context_used": docs,
    }


@app.get("/ask/stream")
def ask_stream(question: str):
    docs, metas = retrieve(question)
    context = "\n\n".join(docs)
    augmented_prompt = ASK_PROMPT.format(context=context, question=question)

    def stream():
        sources = [
            {
                "filename": m.get("source", "?"),
                "line_start": m.get("line_start"),
                "line_end": m.get("line_end"),
                "excerpt": (d[:280] + "…") if len(d) > 280 else d,
            }
            for d, m in zip(docs, metas)
        ]
        yield json.dumps({"type": "sources", "items": sources}) + "\n"
        for chunk in ollama.chat(
            model="gemma4",
            messages=[{"role": "user", "content": augmented_prompt}],
            stream=True,
        ):
            yield (
                json.dumps({"type": "token", "text": chunk["message"]["content"]})
                + "\n"
            )

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
