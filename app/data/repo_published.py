"""The last published daily price table (a single row, id=1)."""
import json
import sqlite3


def replace(conn: sqlite3.Connection, day: str, rows: list) -> None:
    """Store the published rows, replacing the previous ones."""
    conn.execute(
        "INSERT INTO published_daily(id, day, rows_json, published_at) "
        "VALUES (1, ?, ?, datetime('now')) "
        "ON CONFLICT(id) DO UPDATE SET day=excluded.day, "
        "rows_json=excluded.rows_json, published_at=datetime('now')",
        (day, json.dumps(rows, ensure_ascii=False)),
    )
    conn.commit()


def get(conn: sqlite3.Connection) -> dict | None:
    """Return {day, rows, published_at} or None if nothing is published."""
    row = conn.execute(
        "SELECT day, rows_json, published_at FROM published_daily WHERE id=1"
    ).fetchone()
    if row is None:
        return None
    return {"day": row[0], "rows": json.loads(row[1]), "published_at": row[2]}
