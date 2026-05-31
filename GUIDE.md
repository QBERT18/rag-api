# Hosting rag-api on a server with ngrok

Run the whole app in Docker and expose it publicly through ngrok — no domain
needed. Data is stored locally in `./data/`.

## Prerequisites
- A Linux server with Docker + Compose v2 (`docker compose version`).
- A free ngrok account → copy your authtoken:
  https://dashboard.ngrok.com/get-started/your-authtoken

## Steps

```bash
# 1. Clone from GitHub
git clone https://github.com/QBERT18/rag-api.git
cd rag-api

# 2. Create your .env from the example
cp .env.example .env

# 3. Edit .env — set these two values:
#    NGROK_AUTHTOKEN=<your token>
#    FRONTEND_API_BASE=/api
nano .env

# 4. Pull the prebuilt images and start the stack WITH the public tunnel.
#    (Images are built by GitHub Actions and published to GHCR — no local
#     build needed. Use `up -d --build` instead only if you want to build
#     from source on this machine.)
docker compose --profile tunnel pull
docker compose --profile tunnel up -d

# 5. First boot pulls the Ollama models (~3–4 GB) — watch progress:
docker compose logs -f ollama-init      # Ctrl-C when it prints "Models ready."

# 6. Get your public URL (one of):
docker logs rag-ngrok | grep -i "url="   # look for url=https://....ngrok-free.app
#   or open the ngrok inspector:  http://<your-server-ip>:4040
```

Open the printed `https://....ngrok.app` URL in any browser. Create a
workspace, upload documents, ask questions.

## Picking a model for your RAM

The whole stack (Ollama + chat model + embedding model + backend + frontend)
shares the server's RAM. Defaults are tuned for a **~4 GB** box:

| Server RAM | `OLLAMA_CHAT_MODEL` | Notes |
|---|---|---|
| ~4 GB | `gemma3:1b` (default) | ~815 MB model; lowest usable quality. |
| ~2 GB | `qwen2.5:0.5b` | ~400 MB; very small, weaker answers. |
| 8 GB+ | `gemma3:4b` | Much better answers. |

Embedding stays `nomic-embed-text` (~274 MB). If you still hit out-of-memory,
switch it to the tiny `all-minilm` (~46 MB) in `.env` — note this lowers
retrieval quality and requires re-uploading documents (different vector size).

Set the value in `.env` before step 4, e.g. `OLLAMA_CHAT_MODEL=gemma3:1b`.

## Data

Everything persists on the host under `./data/`:
- `./data/ollama`   — downloaded models
- `./data/backend`  — Chroma vector DB + `workspace.db` (workspaces, chats)

Back it up by copying that folder. Deleting it wipes all data.

## Managing the stack

```bash
docker compose --profile tunnel ps             # status
docker compose --profile tunnel logs -f        # all logs
docker compose --profile tunnel down           # stop (keeps ./data)
docker compose --profile tunnel up -d          # start again (no rebuild)
docker compose --profile tunnel pull           # fetch the latest images from GHCR
```

Note: the random ngrok URL changes every restart. Re-run step 6 to get the new one.

## Local-only (no tunnel)

```bash
docker compose up -d --build     # app on http://localhost:3000, no public URL
```

## Continuous deployment (CI/CD)

Pushing to `main` builds both Docker images in **GitHub Actions**, publishes
them to **GHCR**, and the server's **Watchtower** container auto-pulls and
redeploys them. The build happens in the cloud, so your server never builds
(important on a small box).

```
git push main ─► GitHub Actions builds backend + frontend
              ─► pushes ghcr.io/qbert18/rag-api-{backend,frontend}:latest
server: Watchtower polls GHCR ─► pulls :latest ─► recreates the 2 containers
```

### One-time setup (do once)

1. **Land the pipeline** — make sure `.github/workflows/build.yml` and the
   updated `docker-compose.yml` are on `main`:
   ```bash
   git push origin main
   ```
2. **Watch the first build** — GitHub repo → **Actions** tab → wait for the
   `build-and-push` run to go green (~2–4 min).
3. **Make the two images public** so the server can pull without logging in.
   GitHub → profile picture → **Your packages**
   (`https://github.com/QBERT18?tab=packages`). For **each** of
   `rag-api-backend` and `rag-api-frontend`: open it → **Package settings** →
   **Danger Zone** → **Change visibility** → **Public** (confirm by typing the
   name). Optional: **Connect repository** → `rag-api`.
4. **Start the server in pull mode** (Watchtower comes up with the `tunnel`
   profile):
   ```bash
   cd rag-api
   git pull
   docker compose --profile tunnel pull
   docker compose --profile tunnel up -d
   docker logs rag-watchtower --tail 20   # confirms it's watching the 2 containers
   ```

You never build on the server again.

### Daily workflow

1. Code locally, `git push origin main`.
2. Actions builds + pushes new images (~2–4 min).
3. Within ~2 min, Watchtower on the server pulls `:latest` and recreates the
   backend/frontend containers. Nothing to do on the server.
4. Reload the ngrok URL — your change is live.

### Occasional manual cases

- **Changed `docker-compose.yml`, `Caddyfile`, or `.env`** (not code) —
  Watchtower won't apply these; on the server run
  `git pull && docker compose --profile tunnel up -d`.
- **Roll back a bad deploy** — every build also pushes a `sha-<commit>` tag.
  Temporarily set e.g.
  `image: ghcr.io/qbert18/rag-api-frontend:sha-1a2b3c4` and
  `docker compose --profile tunnel up -d frontend`.
- **Force an immediate update check** — `docker restart rag-watchtower`.

## Security

The app has no authentication — anyone with the ngrok URL can use it. The
direct host ports (`8000`, `3000`, `4040`) are also open if your firewall
allows them; restrict them so traffic only enters through ngrok.
