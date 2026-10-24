"""لاگ ممیزی (بدون رمز)."""
import sqlite3


def add_entry(
    conn: sqlite3.Connection, admin_id: int | None, action: str, detail: str = ""
) -> None:
    conn.execute(
        "INSERT INTO audit_log(admin_id, action, detail) VALUES (?,?,?)",
        (admin_id, action, detail),
    )
    conn.commit()


def recent(conn: sqlite3.Connection, limit: int = 20) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    return [dict(r) for r in rows]
