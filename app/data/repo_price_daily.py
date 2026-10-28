"""Daily price history of published auto prices (caller commits)."""
import sqlite3


def record(conn: sqlite3.Connection, day: str, rows: list[dict]) -> int:
    """Save one row per model/year for the day; same day overwrites. No commit."""
    count = 0
    for row in rows:
        conn.execute(
            "INSERT INTO price_daily(day, name, year, price_m) "
            "VALUES (?,?,?,?) "
            "ON CONFLICT(day, name, year) DO UPDATE SET "
            "price_m=excluded.price_m, recorded_at=datetime('now')",
            (day, row["name"], row["year"], row["price_m"]),
        )
        count += 1
    return count


def series(conn: sqlite3.Connection, name: str, year: int) -> list[tuple]:
    """Return (day, price_m) pairs of one model/year, oldest first."""
    cur = conn.execute(
        "SELECT day, price_m FROM price_daily "
        "WHERE name=? AND year=? ORDER BY day",
        (name, year),
    )
    return [(r[0], r[1]) for r in cur.fetchall()]
