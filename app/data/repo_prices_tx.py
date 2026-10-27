"""Our published price per car, written without commit (caller commits)."""
import sqlite3

from app.data.repo_prices import UPSERT, get_price

# The column is NOT NULL with a CHECK; this value is never shown to users.
FIXED_CONFIDENCE = "green"
PUBLISHED = "published"


def sync_price(
    conn: sqlite3.Connection, trim_id: int, year: int, value: int,
    entered_by: int | None, source: str = "photo",
) -> int:
    """Set low=high=value for a selected source; no commit."""
    conn.execute(
        UPSERT.replace(
            "VALUES (?,?,?,?,?,?,?)",
            "VALUES (?,?,?,?,?,?,?,?)",
        ),
        (
            trim_id, year, value, value, FIXED_CONFIDENCE,
            PUBLISHED, entered_by, source,
        ),
    )
    price = get_price(conn, trim_id, year)
    conn.execute(
        "INSERT INTO price_history(price_id, low, high) VALUES (?,?,?)",
        (price.id, value, value),
    )
    return price.id


def sync_auto_price(
    conn: sqlite3.Connection, trim_id: int, year: int, value: int,
) -> int | None:
    """Store an automatic price unless a photo override is active."""
    current = get_price(conn, trim_id, year)
    if current is not None and current.source == "photo":
        return current.id
    return sync_price(conn, trim_id, year, value, None, "auto")

def sync_auto_by_model(
    conn: sqlite3.Connection, model: str, year: int, value: int,
) -> int | None:
    """Store a 1car price for the matching وان‌کار base trim."""
    row = conn.execute(
        "SELECT t.id FROM trims t "
        "JOIN models m ON m.id=t.model_id "
        "JOIN brands b ON b.id=m.brand_id "
        "WHERE b.name=? AND m.name=? AND t.name=?",
        ("وان‌کار", model, "پایه"),
    ).fetchone()
    if row is None:
        return None
    return sync_auto_price(conn, row[0], year, value)
