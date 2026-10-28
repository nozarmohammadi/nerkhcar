"""Check a typed model year against the years found in the table."""
from app.core import model_lookup

GREG_MIN = 1900
OFFSET = 621


def is_greg(year: int) -> bool:
    return year > GREG_MIN


def to_jalali(year: int) -> int:
    """Jalali form of a year that may be Gregorian."""
    return year - OFFSET if is_greg(year) else year


def last_year(rows: list[dict], name: str) -> int | None:
    years = model_lookup.years_of(rows, name)
    return years[0] if years else None


def match_year(rows: list[dict], name: str, year: int) -> int:
    """Express the typed year in the calendar the table uses for this model."""
    last = last_year(rows, name)
    if last is None or is_greg(last) == is_greg(year):
        return year
    return year + OFFSET if is_greg(last) else year - OFFSET


def check_year(rows: list[dict], name: str, year: int) -> str:
    """Return 'ok', 'after_last' or 'unknown_model'.

    The table holds only the newest years, so an older year is allowed.
    """
    last = last_year(rows, name)
    if last is None:
        return "unknown_model"
    return "after_last" if match_year(rows, name, year) > last else "ok"
