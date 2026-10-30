"""Today's price of one car inside the specs flow (published table)."""
from app.adapters.telegram import dbrun
from app.adapters.telegram.texts import specs as t
from app.config import Settings
from app.core import daily_text, price_age, price_lookup, published_date
from app.data import repo_published


def _hit(settings: Settings, name: str):
    """(published data, matching row); data is None when nothing is published."""
    data = dbrun.run(settings, repo_published.get)
    if data is None:
        return None, None
    return data, price_lookup.lookup(data["rows"], name)


def has_price(settings: Settings, name: str) -> bool:
    """True when today's table has a price for this car name."""
    return _hit(settings, name)[1] is not None


def footer_text(settings: Settings, name: str) -> str:
    """Price block under the specs table (fresh / old / missing)."""
    data, hit = _hit(settings, name)
    if data is None:
        return t.NO_PRICE
    age = price_age.status(data["published_at"])
    if age == "expired":
        return t.NO_PRICE
    if hit is None:
        return t.NO_PRICE
    lines = [t.PRICE_HEADER]
    if age == "old":
        lines.append(t.OLD_DATE_LINE.format(
            date=published_date.fa(data["published_at"])))
    lines.append(t.PRICE_LINE.format(
        year=daily_text.fa(hit["year"]),
        price=daily_text.fa(f"{hit['price_m']:,}")))
    lines.append(t.PRICE_NOTE)
    return "\n".join(lines)
