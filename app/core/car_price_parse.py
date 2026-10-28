"""Parse the 1car.ir daily price table (pure logic: no network, no Telegram)."""
import re

from app.core import table_parse

ROW = re.compile(r"<tr.*?</tr>", re.S)
CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)
TAG = re.compile(r"<[^>]+>")
NUMBER = re.compile(r"\d[\d,]*")
PERCENT = re.compile(r"\d+(?:\.\d+)?")
DATE = re.compile(r'"dateModified":\s*"(\d{4}-\d{2}-\d{2})"')
MIN_PRICE = 1_000_000  # ignore numbers below one million toman
MAX_DAILY_PCT = 15  # a bigger daily move is a wide-range artifact
# Column order: name, year, market, factory, dealer, daily change.
COL_NAME, COL_YEAR, COL_MARKET, COL_CHANGE = 0, 1, 2, 5


def _text(html: str) -> str:
    return " ".join(TAG.sub(" ", html).split())


def _numbers(html: str) -> list[int]:
    text = _text(html).translate(table_parse.DIGITS)
    return [int(n.replace(",", "")) for n in NUMBER.findall(text)]


def _market_price(cell: str) -> int | None:
    """Single price, or the midpoint of a range; None when the cell is empty."""
    nums = [n for n in _numbers(cell) if n >= MIN_PRICE]
    if not nums:
        return None
    return (nums[0] + nums[-1]) // 2


def _change(cell: str, price: int) -> int | None:
    """Convert the daily percent change into toman (approximate)."""
    text = _text(cell).translate(table_parse.DIGITS).replace("\u066b", ".")
    found = PERCENT.search(text)
    if not found:
        return None
    pct = float(found.group())
    if "trend-down" in cell or "\u25bc" in cell:
        pct = -pct
    if abs(pct) > MAX_DAILY_PCT:
        return None
    return round(price - price / (1 + pct / 100))


def _year(cell: str) -> int | None:
    nums = _numbers(cell)
    return nums[0] if nums else None


HEAD = re.compile(r"<h[2-4][^>]*>(.*?)</h[2-4]>", re.S)
ROW_OR_HEAD = re.compile(r"<tr.*?</tr>|<h[2-4][^>]*>.*?</h[2-4]>", re.S)
BRAND_PREFIX = re.compile(r"^\u0642[\u06cc\u064a]\u0645\u062a\s+")  # "price" + space


def _row(row: str, brand: str) -> dict | None:
    """One table row with a market price; None for any other row."""
    if "price-range" not in row:
        return None
    cells = CELL.findall(row)
    if len(cells) <= COL_CHANGE:
        return None
    price = _market_price(cells[COL_MARKET])
    if price is None:
        return None
    return {
        "name": _text(cells[COL_NAME]),
        "year": _year(cells[COL_YEAR]),
        "price": price,
        "change": _change(cells[COL_CHANGE], price),
        "brand": brand,
    }


def _heading_brand(chunk: str, current: str) -> str:
    """Brand named by a heading inside this chunk; else the current brand."""
    found = HEAD.search(chunk)
    if not found:
        return current
    title = _text(found.group(1))
    if BRAND_PREFIX.match(title):
        return BRAND_PREFIX.sub("", title).strip()
    return current


def parse_rows(html: str) -> list[dict]:
    """Raw rows (toman) with the brand of the last brand heading above them."""
    out, brand = [], ""
    for found in ROW_OR_HEAD.finditer(html):
        chunk = found.group(0)
        row = _row(chunk, brand)
        if row:
            out.append(row)
        elif "price-range" not in chunk:
            brand = _heading_brand(chunk, brand)
    return out


def to_rows(html: str) -> list[dict]:
    """Normalize parsed rows into the photo-row shape, plus the brand."""
    out = []
    for raw in parse_rows(html):
        row = table_parse.normalize_row(raw)
        row["brand"] = raw["brand"]
        out.append(row)
    return out


def page_date(html: str) -> str | None:
    """Return the page's own modified date (Jalali, YYYY-MM-DD) if present."""
    found = DATE.search(html.translate(table_parse.DIGITS))
    return found.group(1) if found else None
