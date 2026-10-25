"""Download the three price-table pages (network only, no parsing)."""
import logging

import aiohttp

log = logging.getLogger("nerkhcar.fx")
BASE = "https://www.tgju.org/"
PAGES = ("currency", "gold-chart", "coin")
HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = aiohttp.ClientTimeout(total=25)


async def fetch_pages() -> list[str]:
    """Return the HTML of each page that answered 200; failed ones are skipped."""
    out: list[str] = []
    async with aiohttp.ClientSession(headers=HEADERS, timeout=TIMEOUT) as s:
        for page in PAGES:
            try:
                async with s.get(BASE + page) as r:
                    if r.status == 200:
                        out.append(await r.text(errors="ignore"))
                    else:
                        log.warning("fx page failed: %s", r.status)
            except Exception as exc:
                log.warning("fx page error: %s", type(exc).__name__)
    return out
