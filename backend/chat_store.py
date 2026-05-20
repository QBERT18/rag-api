import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from config import settings

_DB_PATH = Path(settings.chat_db_path)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def _row_to_chat(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_message(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "chat_id": row["chat_id"],
        "role": row["role"],
        "content": row["content"],
        "sources": json.loads(row["sources_json"]) if row["sources_json"] else None,
        "created_at": row["created_at"],
    }


def _init_db() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                sources_json TEXT,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_messages_chat_id_id
                ON messages(chat_id, id);

            CREATE INDEX IF NOT EXISTS idx_chats_updated_at
                ON chats(updated_at DESC);
            """
        )


_init_db()


def create_chat(title: str = "New chat") -> dict:
    now = _now()
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO chats (title, created_at, updated_at) VALUES (?, ?, ?)",
            (title, now, now),
        )
        chat_id = cur.lastrowid
        row = conn.execute(
            "SELECT * FROM chats WHERE id = ?", (chat_id,)
        ).fetchone()
        return _row_to_chat(row)


def list_chats() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM chats ORDER BY updated_at DESC, id DESC"
        ).fetchall()
        return [_row_to_chat(r) for r in rows]


def get_chat(chat_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM chats WHERE id = ?", (chat_id,)
        ).fetchone()
        return _row_to_chat(row) if row else None


def rename_chat(chat_id: int, title: str) -> dict | None:
    now = _now()
    with _connect() as conn:
        cur = conn.execute(
            "UPDATE chats SET title = ?, updated_at = ? WHERE id = ?",
            (title, now, chat_id),
        )
        if cur.rowcount == 0:
            return None
        row = conn.execute(
            "SELECT * FROM chats WHERE id = ?", (chat_id,)
        ).fetchone()
        return _row_to_chat(row)


def delete_chat(chat_id: int) -> bool:
    with _connect() as conn:
        cur = conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
        return cur.rowcount > 0


def add_message(
    chat_id: int,
    role: str,
    content: str,
    sources: list[dict] | None = None,
) -> dict:
    now = _now()
    sources_json = json.dumps(sources) if sources else None
    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO messages (chat_id, role, content, sources_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (chat_id, role, content, sources_json, now),
        )
        msg_id = cur.lastrowid
        conn.execute(
            "UPDATE chats SET updated_at = ? WHERE id = ?", (now, chat_id)
        )
        row = conn.execute(
            "SELECT * FROM messages WHERE id = ?", (msg_id,)
        ).fetchone()
        return _row_to_message(row)


def list_messages(chat_id: int) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM messages WHERE chat_id = ? ORDER BY id ASC",
            (chat_id,),
        ).fetchall()
        return [_row_to_message(r) for r in rows]


def recent_messages_for_context(chat_id: int, n: int) -> list[dict]:
    if n <= 0:
        return []
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT role, content FROM messages
            WHERE chat_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (chat_id, n),
        ).fetchall()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]
