"""When to poll the daily car price page (pure logic, no network)."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.core import jalali

START_HOUR = 9
END_HOUR = 15
FRIDAY = 4
TEHRAN = ZoneInfo("Asia/Tehran")
SLOTS = ((11, 30), (12, 30), (13, 30), (14, 30))
FINAL = (14, 30)
GRACE_MIN = 10
TICK_SEC = 300


def jalali_day(now: datetime) -> str:
    """Today's Jalali date as YYYY-MM-DD, like the page's dateModified."""
    jy, jm, jd = jalali.to_jalali(now.year, now.month, now.day)
    return f"{jy:04d}-{jm:02d}-{jd:02d}"


def in_window(now: datetime) -> bool:
    """True on working days between START_HOUR and END_HOUR (Tehran time)."""
    return now.weekday() != FRIDAY and START_HOUR <= now.hour < END_HOUR


def _start(now: datetime, slot: tuple[int, int]) -> datetime:
    """The exact Tehran moment of a slot on the day of `now`."""
    return now.replace(hour=slot[0], minute=slot[1], second=0, microsecond=0)


def due_slot(now: datetime) -> tuple[int, int] | None:
    """The slot whose grace window holds `now` (Tehran time), else None."""
    now = now.astimezone(TEHRAN)
    if now.weekday() == FRIDAY:
        return None
    for slot in SLOTS:
        start = _start(now, slot)
        if start <= now < start + timedelta(minutes=GRACE_MIN):
            return slot
    return None


def seconds_to_next(now: datetime) -> float:
    """Sleep time: up to TICK_SEC, but never past the next slot start."""
    now = now.astimezone(TEHRAN)
    ahead = [(_start(now, s) - now).total_seconds() for s in SLOTS]
    return max(1.0, min([TICK_SEC] + [a for a in ahead if a > 0]))
