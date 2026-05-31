# rag-api

A local-first, NotebookLM-style RAG (retrieval-augmented generation) app you
can run on your own machine. Upload documents into per-topic
**workspaces**, then chat with an LLM that grounds every answer in chunks
from those documents — with inline citations linking back to the source
file and line range.

Everything runs locally:

- **Backend** — FastAPI + Chroma vector store + SQLite chat history.
- **Frontend** — Nuxt 4 + Tailwind v4, dark/light mode, markdown rendering
  with code highlighting.
- **LLM** — [Ollama](https://ollama.com) running locally (CPU or NVIDIA GPU).
  No API keys, no cloud calls.

---

## Features

- 📚 **Workspaces** — each one has its own Chroma collection and chat
  history. Switch contexts instantly; data never leaks between them.
- 🔎 **Hybrid retrieval** — Chroma vector search plus IDF-weighted keyword
  reranking and source-diversity caps, with relevance-thresholded
  citations so off-topic queries don't surface noisy chunks.
- 📎 **Grounded citations** — the assistant's reply lists exactly which
  files (and line ranges) contributed to the answer. Click a chip to
  read the excerpts inline.
- 🌗 **Dark / light theme** — system-aware, persistent, no flash on
  reload.
- ✍️ **Markdown chat** — assistant responses render markdown (GFM
  tables, lists, fenced code blocks with syntax highlighting, links)
  with DOMPurify sanitisation.
- 🛑 **Stop generation** — abort a streaming reply mid-flight; the
  partial response is still saved.
- 🪟 **Resizable split** — drag the divider between Documents and Chat;
  the width persists across reloads.
- 📂 **Many file formats** — `.txt`, `.md`, `.pdf`, `.docx`, `.html`,
  `.csv`, `.json` (extensible via [`backend/parsers`](backend/parsers)).

---

## Quick start (Docker)

> **Prerequisites:** [Docker](https://www.docker.com/) with Compose v2
> (Docker Desktop on macOS/Windows, or Docker Engine + the `compose`
> plugin on Linux). That's it — no Python, no Node, no Ollama install
> on the host.

### 1. Clone the repo

```bash
git clone git@github.com:QBERT18/rag-api.git
cd rag-api
```

### 2. (Optional) pick different models

The defaults are `gemma3:1b` for chat (small enough for a ~4 GB-RAM
server) and `nomic-embed-text` for embeddings. On a bigger machine
`gemma3:4b` gives better answers. To use different ones, copy
`.env.example` to `.env` and edit:

```bash
cp .env.example .env
```

```dotenv
OLLAMA_CHAT_MODEL=llama3.2:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

Any tag from <https://ollama.com/library> works.

### 3. Bring everything up

```bash
docker compose up --build
```

What this does on the first run:

1. Builds the backend image (Python 3.12 + FastAPI deps).
2. Builds the frontend image (Nuxt build → `node .output/server/index.mjs`).
3. Pulls the `ollama/ollama` image.
4. Starts Ollama, waits for its healthcheck.
5. Runs the one-shot `ollama-init` container, which pulls your chat +
   embedding models into the `ollama_data` volume (≈ 3–4 GB on first
   run; cached after).
6. Starts the backend and frontend.

Total cold-start time: a few minutes, mostly the model download.
Subsequent `docker compose up` runs start in seconds because the models
and built images are cached.

### 4. Open the app

[http://localhost:3000](http://localhost:3000)

Click **New workspace**, upload a few documents, ask a question. Citation
chips beneath each reply point at the source file + line range.

### Stopping and starting

```bash
docker compose down       # stop containers, keep volumes (data persists)
docker compose up         # start again, no rebuild needed
docker compose down -v    # wipe ALL data (workspaces, chats, models)
```

### Using a GPU (optional)

If you have an NVIDIA GPU and the
[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
installed, add this block under `ollama:` in [docker-compose.yml](docker-compose.yml):

```yaml
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

Then `docker compose up`. Backend talks to Ollama over HTTP either way.

### Public hosting via ngrok (optional)

To expose the stack on a server without a domain, see
[GUIDE.md](GUIDE.md) — a Caddy reverse proxy behind a single ngrok tunnel,
started with `docker compose --profile tunnel up`.

---

## Manual setup (without Docker)

If you'd rather develop against the source directly, the Makefile handles
both backend and frontend.

### Prerequisites

- **Python 3.12** (see [`backend/.python-version`](backend/.python-version))
- **Node 22+**
- A running **Ollama** instance with your chosen models pulled:
  ```bash
  ollama pull gemma3:1b
  ollama pull nomic-embed-text
  ```

### Install + run

```bash
make venv        # create backend/venv
make install     # install backend deps
cd frontend && npm install && cd ..

make dev         # run backend (:8000) and frontend (:3000) together
```

Other commands:

```bash
make backend     # backend only (auto-reload)
make frontend    # frontend only (HMR)
make kill        # free ports 8000 / 3000
make clean       # wipe backend/chroma_db
```

Backend reads [`backend/.env`](backend/.env.example) for configuration —
copy `backend/.env.example` to `backend/.env` and adjust if your Ollama
runs on a non-default URL.

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama HTTP endpoint (Docker uses `http://ollama:11434` internally). |
| `OLLAMA_CHAT_MODEL` | `gemma3:1b` | Chat model tag (small; bump to `gemma3:4b` if RAM allows). |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model tag. |
| `CHROMA_DB_PATH` | `./chroma_db` | Chroma persistence directory (Docker: `/data/chroma_db` on the `backend_data` volume). |
| `WORKSPACE_DB_PATH` | `./workspace.db` | SQLite path for workspaces + chat history. |
| `CORS_ALLOW_ORIGINS` | `http://localhost:3000` | Comma-separated list. |
| `CONTEXT_HISTORY_MESSAGES` | `8` | How many prior messages to feed back into the LLM prompt. |

---

## Project layout

```
.
├── backend/                FastAPI app
│   ├── main.py             HTTP endpoints (workspaces, ask, documents)
│   ├── retrieval.py        Hybrid scoring + citation filtering
│   ├── workspace_store.py  SQLite layer (workspaces, messages)
│   ├── db.py               Chroma client + per-workspace collections
│   ├── parsers/            Per-format text extractors (pdf, docx, …)
│   ├── config.py           pydantic-settings, reads backend/.env
│   ├── prompts.py          System + context prompt templates
│   └── Dockerfile
├── frontend/               Nuxt 4 app
│   ├── app/
│   │   ├── pages/          index (workspace grid) + workspaces/[id]
│   │   ├── components/     ChatPane, DocumentsPane, WorkspaceCard, …
│   │   ├── composables/    useWorkspaces, useMarkdown, useResizablePane, …
│   │   ├── services/       HTTP clients for the backend API
│   │   └── assets/css/     Tailwind v4 + semantic theme tokens
│   └── Dockerfile
├── debug/                  Sample fixtures + test question lists
├── docker-compose.yml      One-command stack
├── Makefile                Bare-metal dev workflow
└── README.md
```

---

## How the RAG pipeline works

1. **Upload.** A document is parsed by the matching backend parser, split
   into 12-line windows with 2-line overlap, embedded with
   `nomic-embed-text`, and stored in a Chroma collection named
   `ws_{workspace_id}` along with `source` / `chunk_index` /
   `line_start` / `line_end` metadata.
2. **Ask.** The question is optionally split on conjunctions, each
   sub-query hits Chroma for the top 100 candidates, and results are
   merged by best score per chunk.
3. **Rerank.** Each chunk's score is `-distance + KW_WEIGHT *
   idf_keyword_overlap(question, chunk)`. The top 6 chunks are kept,
   capped at 3 per source for diversity.
4. **Filter citations.** Chunks below an absolute score floor or far
   below the best hit are dropped from the citation set (still shown to
   the LLM, just not cited). Off-topic queries surface zero chips.
5. **Expand context.** Adjacent chunks (±1) from the same source are
   pulled in just for LLM context, never cited.
6. **Stream.** Tokens stream over NDJSON; the frontend renders the answer
   as markdown and reveals citation chips with a small staggered
   animation. The assistant message + citations are persisted to SQLite
   in the `finally` block so partial responses survive cancellation.

---

## API (selected endpoints)

| Method | Path | Description |
|---|---|---|
| `POST` | `/workspaces` | Create a workspace. |
| `GET` | `/workspaces` | List workspaces (with `doc_count`). |
| `PATCH` | `/workspaces/{id}` | Rename. |
| `DELETE` | `/workspaces/{id}` | Delete workspace + its Chroma collection + messages. |
| `POST` | `/workspaces/{id}/documents` | Upload a document. |
| `GET` | `/workspaces/{id}/documents` | List documents in the workspace. |
| `DELETE` | `/workspaces/{id}/documents/{filename}` | Remove a document's chunks. |
| `GET` | `/workspaces/{id}/messages` | Full chat history for the workspace. |
| `GET` | `/ask/{id}?question=…` | One-shot answer + sources. |
| `GET` | `/ask/{id}/stream?question=…` | NDJSON token stream + sources + done. |

Swagger UI: <http://localhost:8000/docs> while the backend is running.

---

## Tech stack

- **Backend:** FastAPI, Pydantic v2, Chroma, Ollama Python client,
  pypdf, python-docx, BeautifulSoup, SQLite (WAL mode).
- **Frontend:** Nuxt 4, Vue 3, Tailwind v4 (with `@theme` semantic
  tokens), `@nuxtjs/color-mode`, `@nuxt/icon` (Lucide),
  `marked` + `marked-highlight` + `highlight.js`, `dompurify`.
- **LLM runtime:** Ollama (any model from <https://ollama.com/library>).

---

## Claude Code skills

This repo uses a few [Claude Code](https://claude.com/claude-code) skills,
pinned in [`skills-lock.json`](skills-lock.json). There's no auto-restore
command, so after a fresh clone install them manually:

```bash
npx skills add vercel-labs/agent-skills --skill vercel-react-best-practices
npx skills add vercel-labs/agent-skills --skill vercel-composition-patterns
npx skills add vercel-labs/agent-skills --skill vercel-react-native-skills
npx skills add vercel-labs/next-skills --skill next-best-practices
npx skills add vercel-labs/next-skills --skill next-cache-components
```

---

## License

MIT — see [LICENSE](LICENSE) if present, otherwise treat as MIT.
