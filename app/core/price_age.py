"""Judge how old the published price table is (pure logic)."""
from datetime import datetime, timezone

FMT = "%Y-%m-%d %H:%M:%S"
FRESH_HOURS = 24
MAX_HOURS = 72


def status(published_at: str, now: datetime | None = None) -> str:
    """Return fresh (<=24h), old (24-72h) or expired (>72h)."""
    now = now or datetime.now(timezone.utc)
    then = datetime.strptime(published_at, FMT).replace(tzinfo=timezone.utc)
    hours = (now - then).total_seconds() / 3600
    if hours <= FRESH_HOURS:
        return "fresh"
    return "old" if hours <= MAX_HOURS else "expired"
