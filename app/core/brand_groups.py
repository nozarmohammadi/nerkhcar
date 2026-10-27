"""Group published price rows by brand for the brand buttons (pure logic)."""
from collections import Counter

MAX_BRANDS = 98  # Telegram allows 100 buttons per keyboard


def has_brands(rows: list[dict]) -> bool:
    return any(r.get("brand") for r in rows)


def _order(rows: list[dict]) -> list[str]:
    """Brands in order of first appearance (the source page order)."""
    seen: list[str] = []
    for row in rows:
        brand = row.get("brand") or ""
        if brand and brand not in seen:
            seen.append(brand)
    return seen[:MAX_BRANDS]


def _key(row: dict, shown: list[str]) -> str:
    brand = row.get("brand") or ""
    return brand if brand in shown else ""


def brand_list(rows: list[dict]) -> list[tuple[str, int]]:
    """(brand, row count) per button; '' means other, always last."""
    shown = _order(rows)
    counts = Counter(_key(r, shown) for r in rows)
    items = [(b, counts[b]) for b in shown]
    return items + ([("", counts[""])] if counts[""] else [])


def rows_of(rows: list[dict], index: int) -> list[dict]:
    """Rows of the brand at this button index; empty if it no longer exists."""
    items = brand_list(rows)
    if not 0 <= index < len(items):
        return []
    shown = _order(rows)
    return [r for r in rows if _key(r, shown) == items[index][0]]
