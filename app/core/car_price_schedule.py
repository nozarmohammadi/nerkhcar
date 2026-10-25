"""When to poll the daily car price page (pure logic, no network)."""
from datetime import datetime

from app.core import jalali

START_HOUR = 9
END_HOUR = 18
INTERVAL_MIN = 15
FRIDAY = 4


def jalali_day(now: datetime) -> str:
    """Today's Jalali date as YYYY-MM-DD, like the page's dateModified."""
    jy, jm, jd = jalali.to_jalali(now.year, now.month, now.day)
    return f"{jy:04d}-{jm:02d}-{jd:02d}"


def in_window(now: datetime) -> bool:
    """True on working days between START_HOUR and END_HOUR (Tehran time)."""
    return now.weekday() != FRIDAY and START_HOUR <= now.hour < END_HOUR
