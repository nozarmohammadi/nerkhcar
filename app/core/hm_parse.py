"""Parse hamrah-mechanic price pages (pure logic: no network, no Telegram)."""
import json
import re

NEXT = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)
MILLION = 1_000_000
GREG_OFFSET = 621
JALALI = (1370, 1500)
GREGORIAN = (1990, 2100)


def page_props(html: str) -> dict | None:
    """The pageProps dict of a Next.js page; None when missing or broken."""
    found = NEXT.search(html)
    if not found:
        return None
    try:
        props = json.loads(found.group(1))["props"]["pageProps"]
    except (ValueError, KeyError, TypeError):
        return None
    return props if isinstance(props, dict) else None


def _dicts(node):
    """Every dict nested anywhere inside node."""
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _dicts(value)
    elif isinstance(node, list):
        for value in node:
            yield from _dicts(value)


def model_slugs(props: dict) -> dict[str, str]:
    """{url slug: model name} found on a brand page."""
    return {
        d["modelEnglishName"]: d["modelName"]
        for d in _dicts(props)
        if "modelEnglishName" in d and "modelName" in d
    }


def jalali_year(year) -> int | None:
    """Jalali year; Gregorian years are converted, anything else is None."""
    if not isinstance(year, int) or isinstance(year, bool):
        return None
    if JALALI[0] <= year <= JALALI[1]:
        return year
    if GREGORIAN[0] <= year <= GREGORIAN[1]:
        return year - GREG_OFFSET
    return None


def _row(item: dict) -> dict | None:
    """One price row in the same shape as the 1car rows; None if unusable."""
    price, year = item.get("marketPrice"), jalali_year(item.get("carYear"))
    if year is None or not isinstance(price, (int, float)) or price <= 0:
        return None
    name = " ".join(
        f"{item.get('modelName') or ''} {item.get('carTypeName') or ''}".split())
    if not name:
        return None
    return {
        "name": name, "year": year, "price_m": round(price / MILLION),
        "change_m": None, "brand": item.get("brandName") or "", "flags": [],
    }


def year_rows(props: dict) -> list[dict]:
    """Year-by-year rows of one model page, newest year first."""
    block = props.get("yearsPriceList") or {}
    items = block.get("carPriceOtherYearsDetails") or []
    rows = [r for r in map(_row, items) if r is not None]
    return sorted(rows, key=lambda r: -r["year"])



def latest_rows(rows: list[dict]) -> list[dict]:
    """Keep only the newest year of every name; first-seen order."""
    best: dict[str, dict] = {}
    for row in rows:
        old = best.get(row["name"])
        if old is None or row["year"] > old["year"]:
            best[row["name"]] = row
    return list(best.values())
