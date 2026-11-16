import sqlite3
from datetime import datetime, timezone

from ..config import data_directory
from ..providers.base import Message


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(data_directory() / "history.db")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    return connection


def save_message(conversation_id: str, message: Message) -> None:
    with _connect() as db:
        db.execute(
            "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (
                conversation_id,
                message.role,
                message.content,
                datetime.now(timezone.utc).isoformat(),
            ),
        )


def recent_messages(limit: int = 20) -> list[tuple[str, str, str]]:
    with _connect() as db:
        return db.execute(
            "SELECT conversation_id, role, content FROM messages ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()[::-1]


def clear_history() -> int:
    with _connect() as db:
        cursor = db.execute("DELETE FROM messages")
        return cursor.rowcount
