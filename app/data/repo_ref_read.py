"""Read helpers for reference prices (control values for the quality gate)."""
import sqlite3

LATEST = (
    "SELECT r.source_name, r.low, r.high FROM reference_prices r "
    "WHERE r.trim_id=? AND r.year=? AND r.id = ("
    "SELECT MAX(id) FROM reference_prices "
    "WHERE trim_id=r.trim_id AND year=r.year AND source_name=r.source_name) "
    "ORDER BY r.source_name"
)


def latest_per_source(
    conn: sqlite3.Connection, trim_id: int, year: int
) -> list[tuple[str, int, int]]:
    """Newest reference of each source as (source, low, high)."""
    rows = conn.execute(LATEST, (trim_id, year)).fetchall()
    return [(r["source_name"], r["low"], r["high"]) for r in rows]
