import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from config import settings

_DB_PATH = Path(settings.workspace_db_path)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _new_id() -> str:
    return uuid.uuid4().hex


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def _row_to_workspace(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_message(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "workspace_id": row["workspace_id"],
        "role": row["role"],
        "content": row["content"],
        "sources": json.loads(row["sources_json"]) if row["sources_json"] else None,
        "created_at": row["created_at"],
    }


def _init_db() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS workspaces (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                sources_json TEXT,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_messages_workspace_id_id
                ON messages(workspace_id, id);

            CREATE INDEX IF NOT EXISTS idx_workspaces_updated_at
                ON workspaces(updated_at DESC);
            """
        )


_init_db()


def create_workspace(name: str) -> dict:
    now = _now()
    ws_id = _new_id()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO workspaces (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (ws_id, name, now, now),
        )
        row = conn.execute(
            "SELECT * FROM workspaces WHERE id = ?", (ws_id,)
        ).fetchone()
        return _row_to_workspace(row)


def list_workspaces() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM workspaces ORDER BY updated_at DESC, id DESC"
        ).fetchall()
        return [_row_to_workspace(r) for r in rows]


def get_workspace(workspace_id: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM workspaces WHERE id = ?", (workspace_id,)
        ).fetchone()
        return _row_to_workspace(row) if row else None


def rename_workspace(workspace_id: str, name: str) -> dict | None:
    now = _now()
    with _connect() as conn:
        cur = conn.execute(
            "UPDATE workspaces SET name = ?, updated_at = ? WHERE id = ?",
            (name, now, workspace_id),
        )
        if cur.rowcount == 0:
            return None
        row = conn.execute(
            "SELECT * FROM workspaces WHERE id = ?", (workspace_id,)
        ).fetchone()
        return _row_to_workspace(row)


def delete_workspace(workspace_id: str) -> bool:
    with _connect() as conn:
        cur = conn.execute("DELETE FROM workspaces WHERE id = ?", (workspace_id,))
        return cur.rowcount > 0


def add_message(
    workspace_id: str,
    role: str,
    content: str,
    sources: list[dict] | None = None,
) -> dict:
    now = _now()
    sources_json = json.dumps(sources) if sources else None
    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO messages (workspace_id, role, content, sources_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (workspace_id, role, content, sources_json, now),
        )
        msg_id = cur.lastrowid
        conn.execute(
            "UPDATE workspaces SET updated_at = ? WHERE id = ?", (now, workspace_id)
        )
        row = conn.execute(
            "SELECT * FROM messages WHERE id = ?", (msg_id,)
        ).fetchone()
        return _row_to_message(row)


def list_messages(workspace_id: str) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM messages WHERE workspace_id = ? ORDER BY id ASC",
            (workspace_id,),
        ).fetchall()
        return [_row_to_message(r) for r in rows]


def recent_messages_for_context(workspace_id: str, n: int) -> list[dict]:
    if n <= 0:
        return []
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT role, content FROM messages
            WHERE workspace_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (workspace_id, n),
        ).fetchall()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]
