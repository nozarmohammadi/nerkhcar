"""Decide when the owner needs a car price alert (pure logic)."""
from datetime import datetime

from app.core import car_price_schedule as sched

MAX_FAILS = 3


def alert_kind(
    now: datetime, today: str, saved: bool, fails: int,
    sent: set[tuple[str, str]],
) -> str | None:
    """Return 'fail', 'late' or None; each kind is sent once per day."""
    if fails >= MAX_FAILS and (today, "fail") not in sent:
        return "fail"
    late = (
        now.weekday() != sched.FRIDAY and now.hour >= sched.END_HOUR
        and not saved and (today, "late") not in sent
    )
    return "late" if late else None
