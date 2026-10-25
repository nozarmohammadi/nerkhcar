"""Parse tgju price-table pages into rows. No Telegram or network imports."""
import re

ROW = re.compile(
    r'<tr[^>]*data-market-row="([a-z0-9_]+)"[^>]*data-price="([\d,]+)"[^>]*>'
    r"\s*<th>(.*?)</th>",
    re.S,
)
TAGS = re.compile(r"<[^>]+>")
WANTED = (
    "price_dollar_rl", "price_eur", "geram18", "gold_mini_size",
    "sekee", "sekeb", "nim", "rob", "gerami",
)
RIAL_PER_TOMAN = 10


def parse_page(html: str) -> dict[str, dict]:
    """Return {key: {title, toman}} for the wanted keys found on one page."""
    rows: dict[str, dict] = {}
    for key, price, title in ROW.findall(html):
        if key in WANTED and key not in rows:
            rows[key] = {
                "title": " ".join(TAGS.sub("", title).split()),
                "toman": int(price.replace(",", "")) // RIAL_PER_TOMAN,
            }
    return rows


def parse_pages(pages: list[str]) -> dict[str, dict]:
    """Merge several pages; the first page that has a key wins."""
    merged: dict[str, dict] = {}
    for html in pages:
        for key, row in parse_page(html).items():
            merged.setdefault(key, row)
    return merged
