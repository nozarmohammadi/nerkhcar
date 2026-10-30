"""Reviewed car specs; only rows with reviewed=1 are ever returned."""
import json
import sqlite3

_BASE = (
    "FROM car_specs c "
    "JOIN trims t ON t.id=c.trim_id "
    "JOIN models m ON m.id=t.model_id "
    "WHERE c.reviewed=1"
)


def list_reviewed(conn: sqlite3.Connection) -> list[dict]:
    """Every reviewed car: trim_id, display name, source slug."""
    rows = conn.execute(
        "SELECT c.trim_id AS trim_id, m.name AS name, "
        "c.source_slug AS slug " + _BASE + " ORDER BY m.name"
    ).fetchall()
    return [dict(r) for r in rows]


def get(conn: sqlite3.Connection, trim_id: int) -> dict | None:
    """Name and parsed specs of one reviewed car, or None."""
    row = conn.execute(
        "SELECT m.name AS name, c.source_slug AS slug, c.specs_json AS js " + _BASE
        + " AND c.trim_id=?", (trim_id,)
    ).fetchone()
    if row is None:
        return None
    return {"name": row["name"], "slug": row["slug"],
            "specs": json.loads(row["js"])}
