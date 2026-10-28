"""Group published price rows by brand, in source order (pure logic)."""


def has_brands(rows: list[dict]) -> bool:
    return any(r.get("brand") for r in rows)


def _newest_only(rows: list[dict]) -> list[dict]:
    """Keep only the newest year of every car name (current or last built)."""
    best: dict[str, int] = {}
    for row in rows:
        name = row.get("name")
        best[name] = max(best.get(name, 0), row.get("year") or 0)
    return [r for r in rows if (r.get("year") or 0) == best[r.get("name")]]


def _family_together(rows: list[dict]) -> list[dict]:
    """Same first word sit together; inside it same first two words; first-seen order."""
    heads: dict[str, dict[str, list[dict]]] = {}
    for row in rows:
        words = str(row.get("name") or "").split()
        head = words[0] if words else ""
        sub = " ".join(words[:2])
        heads.setdefault(head, {}).setdefault(sub, []).append(row)
    return [r for subs in heads.values() for fam in subs.values() for r in fam]


def grouped(rows: list[dict]) -> list[tuple[str | None, list[dict]]]:
    """Display order: newest year per name, families together, then brands."""
    return _by_brand(_family_together(_newest_only(rows)))


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
