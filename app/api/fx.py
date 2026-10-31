"""Latest dollar, coin and gold prices (toman) from the bot's fx_cache, read-only."""
import sqlite3
from datetime import datetime, timedelta, timezone

from app.data import repo_fx

MAX_AGE_MIN = int(timedelta(hours=72).total_seconds() // 60)
KEYS = (("dollar", "price_dollar_rl"), ("coin", "sekee"), ("gold", "geram18"))


def _age_min(stamp, now):
    """Minutes since a stored timestamp (naive means UTC); None if unreadable."""
    try:
        when = datetime.fromisoformat(str(stamp))
    except ValueError:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return int((now - when).total_seconds() // 60)


def latest(conn: sqlite3.Connection, now=None) -> dict:
    """Return status ok or empty with rows [{key, toman, age_min}]; old rows are hidden."""
    now = now or datetime.now(timezone.utc)
    stored = {r["symbol"]: r for r in repo_fx.load_rows(conn, tuple(s for _, s in KEYS))}
    rows = []
    for key, symbol in KEYS:
        row = stored.get(symbol)
        age = _age_min(row["fetched_at"], now) if row else None
        if age is None or age > MAX_AGE_MIN:
            continue
        rows.append({"key": key, "toman": row["toman"], "age_min": max(age, 0)})
    return {"status": "ok" if rows else "empty", "rows": rows}
