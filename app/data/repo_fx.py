"""Latest FX, gold and coin prices in toman (table fx_cache)."""
import sqlite3

SOURCE = "web"


def save_rows(conn: sqlite3.Connection, rows: dict[str, int]) -> None:
    """Upsert {symbol: toman}; one commit for all rows."""
    for symbol, toman in rows.items():
        conn.execute(
            "INSERT INTO fx_cache(symbol, value, source, fetched_at) "
            "VALUES (?, ?, ?, datetime('now')) "
            "ON CONFLICT(symbol) DO UPDATE SET value=excluded.value, "
            "source=excluded.source, fetched_at=datetime('now')",
            (symbol, toman, SOURCE),
        )
    conn.commit()


def load_rows(conn: sqlite3.Connection, symbols: tuple[str, ...]) -> list[dict]:
    """Return stored rows in the order of symbols; missing ones are skipped."""
    marks = ",".join("?" * len(symbols))
    found = {
        r[0]: {"symbol": r[0], "toman": int(r[1]), "fetched_at": r[2]}
        for r in conn.execute(
            f"SELECT symbol, value, fetched_at FROM fx_cache "
            f"WHERE symbol IN ({marks})", symbols)
    }
    return [found[s] for s in symbols if s in found]
