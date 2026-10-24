"""شمارش روزانهٔ درخواست‌های هوش مصنوعی."""
import sqlite3


def add_request(conn: sqlite3.Connection, day: str) -> None:
    conn.execute(
        "INSERT INTO ai_usage(day, count, last_at) VALUES (?, 1, datetime('now')) "
        "ON CONFLICT(day) DO UPDATE SET count=count+1, last_at=datetime('now')",
        (day,),
    )
    conn.commit()


def get_count(conn: sqlite3.Connection, day: str) -> int:
    row = conn.execute("SELECT count FROM ai_usage WHERE day=?", (day,)).fetchone()
    return row[0] if row else 0
