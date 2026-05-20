# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Top-level `Makefile` handles both backend and frontend (Windows/Unix branches inside). Run from repo root:

- `make venv` — create `backend/venv`
- `make install` — install backend deps into venv
- `make backend` — FastAPI dev server on `:8000` (Swagger at `/docs`)
- `make frontend` — Nuxt dev server on `:3000`
- `make dev` — run both in parallel (`make -j2`)
- `make kill` — free ports 8000/3000
- `make clean` — wipe `backend/chroma_db`

No test suite, linter, or formatter is configured. Backend has no `__init__.py` at root — `uvicorn` is invoked from inside `backend/`, so imports like `from config import settings` resolve. Don't add package-style imports (`from backend.config ...`); they break the dev server.

External dependency: a running **Ollama** instance with the configured chat + embedding models pulled (defaults `gemma4` and `nomic-embed-text`). The app will fail at request time, not import time, if Ollama is unreachable.

## Configuration

Backend reads `backend/.env` via `pydantic-settings` ([backend/config.py](backend/config.py)). See [backend/.env.example](backend/.env.example) for keys. `CORS_ALLOW_ORIGINS` is a comma-separated string parsed into a list by a custom validator. `.env.example` has two stale keys (`CHROMA_COLLECTION_NAME`, `CHAT_DB_PATH`) that no longer match `Settings`; the real names are workspace-scoped (`WORKSPACE_DB_PATH`) and collections are derived per-workspace.

Frontend API base URL is **hardcoded** to `http://localhost:8000` in [frontend/app/services/chat.ts](frontend/app/services/chat.ts), [frontend/app/services/workspaces.ts](frontend/app/services/workspaces.ts), and [frontend/app/services/documents.ts](frontend/app/services/documents.ts) — not env-driven yet.

## Architecture

### Workspace model

A **workspace** is the unit of isolation. Each workspace owns:
- Its own Chroma collection, named `ws_{workspace_id}` ([backend/db.py:16](backend/db.py#L16)).
- Its own message history rows in the shared SQLite DB (`backend/workspace.db`), scoped by `workspace_id` FK with `ON DELETE CASCADE`.

Workspaces are created/listed/renamed/deleted via `/workspaces` ([backend/main.py:63-97](backend/main.py#L63-L97)). Deletion removes both the SQLite rows and the Chroma collection.

### Request flow (`/ask/{workspace_id}/stream`)

1. Load last `N` messages (`context_history_messages`, default 8) for context ([backend/workspace_store.py:166](backend/workspace_store.py#L166)).
2. Persist the user message immediately.
3. Retrieve relevant chunks via `retrieve(workspace_id, question)` ([backend/retrieval.py:123](backend/retrieval.py#L123)).
4. Build the prompt: system prompt → history → `CONTEXT_TEMPLATE` filled with retrieved context + question.
5. Stream tokens from Ollama as NDJSON: `{type:"sources"}` first, then `{type:"token"}` per chunk, finally `{type:"done", message_id}`.
6. Assistant message + sources are persisted in the `finally` block, so partial responses are still saved.

`/ask/{workspace_id}` (non-stream) follows the same flow without streaming. Both endpoints use **GET with query params** — keep that contract or the frontend's `streamAsk` ([frontend/app/services/chat.ts:46](frontend/app/services/chat.ts#L46)) will break.

### Retrieval ([backend/retrieval.py](backend/retrieval.py))

Hybrid scoring on top of Chroma vector search, with several deliberate steps:
- **Query splitting**: splits on `, and` / ` and ` / `; ` to handle compound questions; each subquery is retrieved separately and results are merged by max score per chunk id.
- **Reranking**: `-distance + KW_WEIGHT * keyword_overlap` where keyword overlap is IDF-weighted token intersection between query and chunk. Stopwords are filtered.
- **Source diversity**: caps `MAX_PER_SOURCE=4` chunks per file in the top-K window (`TOP_K=6`).
- **Neighbor expansion**: after top-K is chosen, adjacent chunks (by `chunk_index`, radius 1, capped at `MAX_NEIGHBORS=4`) from the same source are fetched and appended for additional context. This relies on chunk IDs having the form `{source}::chunk{i}` — preserved by the uploader at [backend/main.py:186](backend/main.py#L186).

### Document ingestion + parsers

`POST /workspaces/{id}/documents` runs `get_parser(filename)` ([backend/parsers/__init__.py](backend/parsers/__init__.py)) which dispatches by extension to one of: text, markdown, pdf, docx, html/htm, csv, json. Each parser subclasses `BaseParser` ([backend/parsers/base.py](backend/parsers/base.py)) and only implements `extract_text(bytes) -> str` — chunking is shared in the base class: 12-line windows with 2-line overlap, preserving `line_start`/`line_end` metadata so citations point at original line ranges.

To add a new format: implement `extract_text`, set the `extension` class attr, register in `_REGISTRY`.

### Persistence

- **SQLite** (`backend/workspace.db`, WAL mode, FKs on): two tables, `workspaces` and `messages`. `messages.sources_json` is a JSON-encoded list of citation dicts. `add_message` also bumps `workspaces.updated_at` so the list endpoint is sorted by recency. Schema is created in `_init_db()` on import ([backend/workspace_store.py:48](backend/workspace_store.py#L48)).
- **Chroma** persistent client at `chroma_db_path`. The Ollama embedding function is attached per collection.

### Frontend (Nuxt 4)

- Pages: `pages/index.vue` (workspace grid) → `pages/workspaces/[id].vue` (split view: `DocumentsPane` + `ChatPane`).
- State: `useWorkspaces()` ([frontend/app/composables/useWorkspaces.ts](frontend/app/composables/useWorkspaces.ts)) is a **module-scoped singleton** — `workspaces` is defined at module top-level, not inside the composable, so all components share the same reactive list. Mutations bump `updated_at` on the server but the composable doesn't refetch; `bumpToTop` exists for client-side reordering.
- Streaming chat reads the NDJSON response in `streamAsk` and dispatches `sources` / `token` / `done` events to the caller.
- Styling: Tailwind v4 via `@tailwindcss/vite`; no `tailwind.config.*` file — config is inferred from `assets/css/main.css`.

## Repo state notes

- `backend/chat_store.py` (deleted) was the single-conversation predecessor of `workspace_store.py`. References to "chat" in the env example are leftovers.
- `backend/workspace.db*` files are present in the working tree and uncommitted — treat the local DB as ephemeral dev data, not source of truth.
- The `debug/` directory at repo root holds scratch artifacts; not part of the app.
