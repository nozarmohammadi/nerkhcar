"""Find today's price of one car by its name (pure logic)."""
from app.core import my_car_input


def lookup(rows: list[dict], name: str) -> dict | None:
    """Newest-year row with a price whose name equals `name`; else None."""
    key = my_car_input.norm(name)
    hits = [
        r for r in rows
        if r.get("price_m") and my_car_input.norm(r.get("name") or "") == key
    ]
    if not hits:
        return None
    return max(hits, key=lambda r: r.get("year") or 0)
