"""Read-only SQLite access for the API layer."""
import sqlite3
from pathlib import Path


def connect_ro(path) -> sqlite3.Connection:
    """Open the database so that no write can ever happen."""
    conn = sqlite3.connect(f"file:{Path(path)}?mode=ro", uri=True, timeout=5)
    conn.execute("PRAGMA query_only=ON")
    return conn
