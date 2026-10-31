"""Read the last published daily price table; never show stale prices."""
import json
import sqlite3
from datetime import datetime, timedelta, timezone

MAX_AGE = timedelta(hours=72)


def _parse(stamp):
    """Parse a stored timestamp; naive values count as UTC. None if unknown."""
    try:
        when = datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
    except ValueError:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when


def daily(conn: sqlite3.Connection, now=None) -> dict:
    """Return status ok, stale or empty with the published rows."""
    now = now or datetime.now(timezone.utc)
    row = conn.execute(
        "SELECT day, rows_json, published_at, source FROM published_daily WHERE id=1"
    ).fetchone()
    if row is None:
        return {"status": "empty", "rows": []}
    day, rows_json, stamp, source = row
    when = _parse(stamp)
    if when is not None and now - when > MAX_AGE:
        return {"status": "stale", "day": day, "published_at": stamp, "rows": []}
    return {
        "status": "ok", "day": day, "published_at": stamp, "source": source,
        "age_known": when is not None, "rows": json.loads(rows_json),
    }
