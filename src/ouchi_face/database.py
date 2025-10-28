from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = BASE_DIR / "data" / "ouchi_face.db"


def get_database_path() -> Path:
    env_path = os.getenv("OUCHI_FACE_DB_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_DB_PATH


def ensure_database() -> None:
    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                description TEXT NOT NULL,
                link_url TEXT,
                location TEXT,
                icon_url TEXT,
                repo_url TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    ensure_database()
    connection = sqlite3.connect(get_database_path())
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()
