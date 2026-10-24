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


def ensure_owner(conn: sqlite3.Connection, owner_id: int) -> bool:
    """مالک را از .env ثبت می‌کند (بدون رمز). اگر تازه ساخته شد True."""
    if get_admin(conn, owner_id):
        return False
    add_admin(conn, owner_id, "owner")
    return True


def set_password(conn: sqlite3.Connection, tg_id: int, pw_hash: str) -> None:
    conn.execute(
        "UPDATE admins SET pw_hash=?, must_change=0, failed_count=0 WHERE tg_id=?",
        (pw_hash, tg_id),
    )
    conn.commit()


def save_auth_state(
    conn: sqlite3.Connection, tg_id: int, failed_count: int,
    locked_until: str | None, session_until: str | None,
) -> None:
    conn.execute(
        "UPDATE admins SET failed_count=?, locked_until=?, session_until=? "
        "WHERE tg_id=?",
        (failed_count, locked_until, session_until, tg_id),
    )
    conn.commit()
