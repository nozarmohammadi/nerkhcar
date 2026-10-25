"""Download the 1car.ir daily price page and keep the last raw copies."""
import logging
from datetime import date
from pathlib import Path

import aiohttp

from app.core import car_price_parse

log = logging.getLogger("nerkhcar.carprice")
URL = "https://1car.ir/price"
RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw_prices"
KEEP = 7
MIN_BYTES = 100_000
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "fa,en;q=0.8",
}
TIMEOUT = aiohttp.ClientTimeout(total=30)


def looks_valid(html: str) -> bool:
    """A real page is big and has price rows; this rejects error pages."""
    return len(html) >= MIN_BYTES and "price-range" in html


async def fetch_page() -> str | None:
    """One plain GET; return the HTML, or None on any failure."""
    try:
        async with aiohttp.ClientSession(headers=HEADERS, timeout=TIMEOUT) as s:
            async with s.get(URL) as r:
                if r.status != 200:
                    log.warning("car price page failed: %s", r.status)
                    return None
                html = await r.text(errors="ignore")
    except Exception as exc:
        log.warning("car price page error: %s", type(exc).__name__)
        return None
    if not looks_valid(html):
        log.warning("car price page looks wrong")
        return None
    return html


def prune(folder: Path, keep: int = KEEP) -> None:
    """Delete the oldest raw files, keeping the newest `keep`."""
    files = sorted(folder.glob("price-*.html"), key=lambda p: p.stat().st_mtime)
    for old in files[:-keep]:
        old.unlink()


def save_raw(html: str, folder: Path = RAW_DIR, keep: int = KEEP) -> Path:
    """Save the page as price-<page date>.html, then rotate old files."""
    folder.mkdir(parents=True, exist_ok=True)
    day = car_price_parse.page_date(html) or date.today().isoformat()
    path = folder / f"price-{day}.html"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(html, encoding="utf-8")
    tmp.replace(path)
    prune(folder, keep)
    return path


async def fetch_and_store() -> Path | None:
    """Download once and store; None when the download failed."""
    html = await fetch_page()
    return None if html is None else save_raw(html)
