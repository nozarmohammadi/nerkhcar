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
    """Store a 1car price and create its catalog records when needed."""
    conn.execute(
        "INSERT OR IGNORE INTO brands(name) VALUES (?)",
        ("وان‌کار",),
    )
    brand = conn.execute(
        "SELECT id FROM brands WHERE name=?", ("وان‌کار",)
    ).fetchone()
    if brand is None:
        return None

    conn.execute(
        "INSERT OR IGNORE INTO models(brand_id, name) VALUES (?, ?)",
        (brand[0], model),
    )
    model_row = conn.execute(
        "SELECT id FROM models WHERE brand_id=? AND name=?",
        (brand[0], model),
    ).fetchone()
    if model_row is None:
        return None

    conn.execute(
        "INSERT OR IGNORE INTO trims(model_id, name) VALUES (?, ?)",
        (model_row[0], "پایه"),
    )
    trim = conn.execute(
        "SELECT id FROM trims WHERE model_id=? AND name=?",
        (model_row[0], "پایه"),
    ).fetchone()
    if trim is None:
        return None

    return sync_auto_price(conn, trim[0], year, value)
