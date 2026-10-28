"""Turn the downloaded 1car.ir page into publishable rows (pure logic)."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.core import car_price_parse, ref_import

TEHRAN = ZoneInfo("Asia/Tehran")
FMT = "%Y-%m-%d %H:%M:%S"
MIN_M = 100  # million toman
MAX_M = 100_000  # wider than photo import: this data comes from the site


def auto_rows(html: str) -> list[dict]:
    """Rows with a valid name, Jalali year and price; the photo range flag is ignored."""
    out = []
    for row in car_price_parse.to_rows(html):
        flags = set(row["flags"]) - {"range"}

        # Imported vehicles keep their Gregorian year; only the flag goes.
        flags.discard("greg_year")

        if flags & ref_import.BLOCKING:
            continue
        if MIN_M <= row["price_m"] <= MAX_M:
            row["flags"] = sorted(flags)
            out.append(row)
    return out


def stamp_and_day(moment: datetime) -> tuple[str, str]:
    """UTC stamp for the database and the Tehran date (ISO) of that moment."""
    utc = moment.astimezone(timezone.utc)
    return utc.strftime(FMT), moment.astimezone(TEHRAN).date().isoformat()
