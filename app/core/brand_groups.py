"""Group published price rows by brand, in source order (pure logic)."""


def has_brands(rows: list[dict]) -> bool:
    return any(r.get("brand") for r in rows)


def grouped(rows: list[dict]) -> list[tuple[str | None, list[dict]]]:
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
