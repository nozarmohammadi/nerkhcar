"""Merge many source brands into a few display groups (pure logic)."""
from app.core import brand_groups, my_car_input


def _lookup(groups: tuple) -> dict[str, int]:
    return {
        my_car_input.norm(brand): index
        for index, (_, brands) in enumerate(groups) for brand in brands
    }


def names(groups: tuple, other: str) -> list[str]:
    """Group names by index; the last entry names the unmapped rows."""
    return [name for name, _ in groups] + [other]


def split(rows: list[dict], groups: tuple) -> list[list[dict]]:
    """Original rows per group in group order; the last list is unmapped."""
    lookup = _lookup(groups)
    out: list[list[dict]] = [[] for _ in range(len(groups) + 1)]
    for row in rows:
        key = my_car_input.norm(row.get("brand") or "")
        out[lookup.get(key, len(groups))].append(row)
    return out


def menu(
    rows: list[dict], groups: tuple, current_year: int | None = None
) -> list[tuple[int, int]]:
    """(group index, shown row count) of every non-empty group.

    Counts exactly the rows the table shows (same filter as the table).
    """
    shown = brand_groups.visible(
        [r for r in rows if r.get("price_m")], current_year)
    return [(i, len(p)) for i, p in enumerate(split(shown, groups)) if p]


def regroup(rows: list[dict], groups: tuple, other: str = "") -> list[dict]:
    """Copy rows with brand = group name (`other` if unmapped), in group order.

    Rows of a table without any brand info are returned untouched.
    """
    if not brand_groups.has_brands(rows):
        return rows
    label = names(groups, other)
    out: list[dict] = []
    for index, part in enumerate(split(rows, groups)):
        out += [{**row, "brand": label[index]} for row in part]
    return out
