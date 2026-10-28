"""Read typed answers of the 'my car' form (pure logic)."""
from app.core import table_parse

MAX_RESULTS = 8
MIN_YEAR = 1370
MAX_KM = 1_500_000
GREG_MIN = 1990
GREG_OFFSET = 621
_SAME = str.maketrans({"\u064a": "\u06cc", "\u0643": "\u06a9", "\u0629": "\u0647", "\u200c": " "})


def norm(text: str) -> str:
    """Lowercase, unify Arabic/Persian letters, collapse spaces."""
    return " ".join(text.translate(_SAME).lower().split())


def search(names: list[str], query: str) -> list[str]:
    """Names containing the query, at most MAX_RESULTS; empty if no query."""
    q = norm(query)
    if len(q) < 2:
        return []
    return [n for n in names if q in norm(n)][:MAX_RESULTS]


def read_year(text: str, current: int) -> int | None:
    """A model year between MIN_YEAR and the current year, else None."""
    year = table_parse.to_int(text)
    ok = year is not None and (
        MIN_YEAR <= year <= current
        or GREG_MIN <= year <= current + GREG_OFFSET)
    if not ok:
        return None
    return year


def read_km(text: str) -> int | None:
    """Mileage in km, 0 up to MAX_KM, else None."""
    km = table_parse.to_int(text)
    if km is None or not 0 <= km <= MAX_KM:
        return None
    return km
