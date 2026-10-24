"""Daily price batches: drafts that survive restarts."""
import json
import sqlite3

DRAFT = "draft"
SENT = "sent"
CANCELLED = "cancelled"
_STATUSES = (DRAFT, SENT, CANCELLED)


def create_draft(conn: sqlite3.Connection, admin_id: int, day: str) -> int:
    cur = conn.execute(
        "INSERT INTO daily_batches(admin_id, day) VALUES (?, ?)", (admin_id, day)
    )
    conn.commit()
    return cur.lastrowid


def find_draft(conn: sqlite3.Connection, admin_id: int, day: str) -> dict | None:
    row = conn.execute(
        "SELECT id, photos, rows_json FROM daily_batches "
        "WHERE admin_id=? AND day=? AND status='draft' ORDER BY id DESC LIMIT 1",
        (admin_id, day),
    ).fetchone()
    if row is None:
        return None
    return {"id": row[0], "photos": row[1], "rows": json.loads(row[2])}


def save_rows(conn: sqlite3.Connection, batch_id: int, rows: list, photos: int) -> None:
    conn.execute(
        "UPDATE daily_batches SET rows_json=?, photos=?, updated_at=datetime('now') "
        "WHERE id=? AND status='draft'",
        (json.dumps(rows, ensure_ascii=False), photos, batch_id),
    )
    conn.commit()


def set_status(conn: sqlite3.Connection, batch_id: int, status: str) -> None:
    if status not in _STATUSES:
        raise ValueError(f"bad status: {status}")
    conn.execute(
        "UPDATE daily_batches SET status=?, updated_at=datetime('now') WHERE id=?",
        (status, batch_id),
    )
    conn.commit()
