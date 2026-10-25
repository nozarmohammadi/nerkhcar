"""Our published price per car, written without commit (caller commits)."""
import sqlite3

from app.data.repo_prices import UPSERT, get_price

# The column is NOT NULL with a CHECK; this value is never shown to users.
FIXED_CONFIDENCE = "green"
PUBLISHED = "published"


def sync_price(
    conn: sqlite3.Connection, trim_id: int, year: int, value: int,
    entered_by: int | None,
) -> int:
    """Set low=high=value as published and add a history row; no commit."""
    conn.execute(
        UPSERT,
        (trim_id, year, value, value, FIXED_CONFIDENCE, PUBLISHED, entered_by),
    )
    price = get_price(conn, trim_id, year)
    conn.execute(
        "INSERT INTO price_history(price_id, low, high) VALUES (?,?,?)",
        (price.id, value, value),
    )
    return price.id
