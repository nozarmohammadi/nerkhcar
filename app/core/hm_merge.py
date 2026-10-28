"""Pick the hamrah-mechanic models and rows that 1car lacks (pure logic)."""
from app.core import car_price_publish as pub, my_car_input


def missing_slugs(models: dict[str, str], ours: list[str]) -> list[str]:
    """Slugs whose model name matches no 1car row (substring on normalized text)."""
    return [
        slug for slug, name in models.items()
        if not any(my_car_input.norm(name) in own for own in ours)
    ]


def dedupe(rows: list[dict]) -> list[dict]:
    """Keep the first row of every (name, year); order is preserved."""
    seen: set[tuple[str, int]] = set()
    out = []
    for row in rows:
        key = (my_car_input.norm(row["name"]), row["year"])
        if key not in seen:
            seen.add(key)
            out.append(row)
    return out


def valid(rows: list[dict]) -> list[dict]:
    """Rows whose price lies inside the same limits as the 1car rows."""
    return [r for r in rows if pub.MIN_M <= r["price_m"] <= pub.MAX_M]
