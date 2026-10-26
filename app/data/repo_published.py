"""The last published daily price table (a single row, id=1)."""
import json
import sqlite3

PHOTO = "photo"
AUTO = "auto"


def replace(
    conn: sqlite3.Connection, day: str, rows: list,
    source: str = PHOTO, published_at: str | None = None,
) -> None:
    """Store the published rows, replacing the previous ones."""
    conn.execute(
        "INSERT INTO published_daily(id, day, rows_json, published_at, source) "
        "VALUES (1, ?, ?, COALESCE(?, datetime('now')), ?) "
        "ON CONFLICT(id) DO UPDATE SET day=excluded.day, "
        "rows_json=excluded.rows_json, published_at=excluded.published_at, "
        "source=excluded.source",
        (day, json.dumps(rows, ensure_ascii=False), published_at, source),
    )
    conn.commit()


def replace_auto(
    conn: sqlite3.Connection, day: str, rows: list, published_at: str
) -> bool:
    """Publish auto rows unless a photo of this day (or newer auto) is live."""
    row = conn.execute(
        "SELECT day, source, published_at FROM published_daily WHERE id=1"
    ).fetchone()
    if row is not None:
        if row[1] == PHOTO and row[0] >= day:
            return False
        if row[1] == AUTO and row[2] > published_at:
            return False
    replace(conn, day, rows, AUTO, published_at)
    return True


def get_source(conn: sqlite3.Connection) -> str | None:
    """Return 'photo' or 'auto', or None if nothing is published."""
    row = conn.execute("SELECT source FROM published_daily WHERE id=1").fetchone()
    return None if row is None else row[0]


def get(conn: sqlite3.Connection) -> dict | None:
    """Return {day, rows, published_at} or None if nothing is published."""
    row = conn.execute(
        "SELECT day, rows_json, published_at FROM published_daily WHERE id=1"
    ).fetchone()
    if row is None:
        return None
    return {"day": row[0], "rows": json.loads(row[1]), "published_at": row[2]}
