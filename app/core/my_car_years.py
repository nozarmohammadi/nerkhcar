"""Check a typed model year against the years found in the table."""
from app.core import model_lookup


def check_year(rows: list[dict], name: str, year: int) -> str:
    """Return 'ok', 'after_last' or 'unknown_model'.

    The table holds only the newest years, so an older year is allowed.
    """
    years = model_lookup.years_of(rows, name)
    if not years:
        return "unknown_model"
    return "after_last" if year > years[0] else "ok"


def last_year(rows: list[dict], name: str) -> int | None:
    years = model_lookup.years_of(rows, name)
    return years[0] if years else None
