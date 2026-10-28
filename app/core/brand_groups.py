"""Group published price rows by brand, in source order (pure logic)."""
from datetime import datetime

from app.core import jalali

# A car is shown only if its newest year is at most this many years old.
# Older cars have no zero-km market price (the table shows a used price).
MAX_AGE = 1
GREG_MIN = 1900
GREG_OFFSET = 621


def _jalali_year(year: int) -> int:
    """Row years may be Gregorian for imported cars; return the Jalali year."""
    return year - GREG_OFFSET if year >= GREG_MIN else year


def _current_year() -> int:
    """Current Jalali year, taken from the date."""
    now = datetime.now()
    return jalali.to_jalali(now.year, now.month, now.day)[0]


def has_brands(rows: list[dict]) -> bool:
    return any(r.get("brand") for r in rows)


def _newest_only(rows: list[dict], current_year: int | None = None) -> list[dict]:
    """Keep only the newest year of every name, and only if it is recent.

    Rows without a year are kept (nothing to judge them by).
    """
    current = current_year or _current_year()
    best: dict[str, int] = {}
    for row in rows:
        name = row.get("name")
        best[name] = max(best.get(name, 0), row.get("year") or 0)
    out = []
    for r in rows:
        year = r.get("year") or 0
        if year != best[r.get("name")]:
            continue
        if year and current - _jalali_year(year) > MAX_AGE:
            continue
        out.append(r)
    return out


def _family_together(rows: list[dict]) -> list[dict]:
    """Same first word sit together; inside it same first two words; first-seen order."""
    heads: dict[str, dict[str, list[dict]]] = {}
    for row in rows:
        words = str(row.get("name") or "").split()
        head = words[0] if words else ""
        sub = " ".join(words[:2])
        heads.setdefault(head, {}).setdefault(sub, []).append(row)
    return [r for subs in heads.values() for fam in subs.values() for r in fam]


def grouped(
    rows: list[dict], current_year: int | None = None
) -> list[tuple[str | None, list[dict]]]:
    """Display order: newest year per name, families together, then brands."""
    return _by_brand(_family_together(_newest_only(rows, current_year)))


def _by_brand(rows: list[dict]) -> list[tuple[str | None, list[dict]]]:
    """(brand, rows) per brand in source order; '' = no brand, always last.

    When no row has a brand at all, one group with brand None (plain table).
    """
    if not has_brands(rows):
        return [(None, rows)]
    buckets: dict[str, list[dict]] = {}
    for row in rows:
        buckets.setdefault(row.get("brand") or "", []).append(row)
    named = [(b, g) for b, g in buckets.items() if b]
    return named + ([("", buckets[""])] if "" in buckets else [])
