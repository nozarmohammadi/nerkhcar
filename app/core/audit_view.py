"""آماده‌سازی لاگ ممیزی برای نمایش (بدون متن فارسی)."""
import sqlite3

from app.data import repo_audit

PAGE = 10
DETAIL_MAX = 40


def recent_rows(conn: sqlite3.Connection, limit: int = PAGE) -> list[dict]:
    rows = []
    for r in repo_audit.recent(conn, limit):
        who = "-" if r["admin_id"] is None else str(r["admin_id"])
        rows.append({
            "at": str(r["at"])[5:16],
            "who": who,
            "action": r["action"],
            "detail": str(r["detail"])[:DETAIL_MAX],
        })
    return rows
