"""Base price of used cars per trim and year (million toman)."""
import sqlite3


def upsert(conn: sqlite3.Connection, trim_id: int, year: int, price: int,
           samples: int, liquidity: str, entered_by: int | None) -> None:
    """Insert or update the base price for a trim and year; commits."""
    conn.execute(
        "INSERT INTO used_base(trim_id, year, price, samples, liquidity, "
        "entered_by) VALUES (?,?,?,?,?,?) "
        "ON CONFLICT(trim_id, year) DO UPDATE SET price=excluded.price, "
        "samples=excluded.samples, liquidity=excluded.liquidity, "
        "entered_by=excluded.entered_by, updated_at=datetime('now')",
        (trim_id, year, price, samples, liquidity, entered_by),
    )
    conn.commit()


def get(conn: sqlite3.Connection, trim_id: int, year: int) -> dict | None:
    """Return {price, samples, liquidity, updated_at} or None."""
    row = conn.execute(
        "SELECT price, samples, liquidity, updated_at FROM used_base "
        "WHERE trim_id=? AND year=?",
        (trim_id, year),
    ).fetchone()
    return None if row is None else dict(row)
