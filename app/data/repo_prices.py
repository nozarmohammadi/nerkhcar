"""قیمت‌ها و تاریخچه‌شان."""
import sqlite3

from app.data.models import Price

UPSERT = (
    "INSERT INTO prices(trim_id, year, low, high, confidence, status, entered_by) "
    "VALUES (?,?,?,?,?,?,?) "
    "ON CONFLICT(trim_id, year) DO UPDATE SET low=excluded.low, "
    "high=excluded.high, confidence=excluded.confidence, "
    "status=excluded.status, entered_by=excluded.entered_by, "
    "updated_at=datetime('now'), confirmed_at=NULL"
)


def upsert_price(
    conn: sqlite3.Connection, trim_id: int, year: int, low: int, high: int,
    confidence: str, status: str, entered_by: int | None,
) -> int:
    conn.execute(UPSERT, (trim_id, year, low, high, confidence, status, entered_by))
    price = get_price(conn, trim_id, year)
    conn.execute(
        "INSERT INTO price_history(price_id, low, high) VALUES (?,?,?)",
        (price.id, low, high),
    )
    conn.commit()
    return price.id


def get_price(conn: sqlite3.Connection, trim_id: int, year: int) -> Price | None:
    row = conn.execute(
        "SELECT * FROM prices WHERE trim_id=? AND year=?", (trim_id, year)
    ).fetchone()
    return Price(**dict(row)) if row else None
