"""Date and time of a published table, in Tehran time. No Telegram imports."""
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from app.core import daily_text

TEHRAN = ZoneInfo("Asia/Tehran")


def parts(data: dict, texts) -> tuple[str, datetime]:
    """Return (Persian date text, Tehran datetime) of the stored publish time."""
    raw = datetime.strptime(data["published_at"], "%Y-%m-%d %H:%M:%S")
    local = raw.replace(tzinfo=timezone.utc).astimezone(TEHRAN)
    day = date(local.year, local.month, local.day)
    return daily_text.date_text(texts, day), local
