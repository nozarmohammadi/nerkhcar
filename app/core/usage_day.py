"""روز سهمیهٔ گوگل: نیمه‌شب به وقت پاسیفیک ریست می‌شود."""
from datetime import datetime
from zoneinfo import ZoneInfo

PACIFIC = ZoneInfo("America/Los_Angeles")


def pacific_day(now: datetime | None = None) -> str:
    now = now or datetime.now(PACIFIC)
    return now.astimezone(PACIFIC).strftime("%Y-%m-%d")
