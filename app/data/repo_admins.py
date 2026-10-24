"""دسترسی به جدول ادمین‌ها."""
import sqlite3

from app.data.models import Admin


def get_admin(conn: sqlite3.Connection, tg_id: int) -> Admin | None:
    row = conn.execute("SELECT * FROM admins WHERE tg_id=?", (tg_id,)).fetchone()
    return Admin(**dict(row)) if row else None


def add_admin(
    conn: sqlite3.Connection, tg_id: int, role: str, pw_hash: str | None = None
) -> None:
    conn.execute(
        "INSERT INTO admins(tg_id, role, pw_hash) VALUES (?,?,?)",
        (tg_id, role, pw_hash),
    )
    conn.commit()
