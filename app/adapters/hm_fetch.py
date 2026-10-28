"""Download hamrah-mechanic brand and model pages (network only)."""
import asyncio
import logging
from urllib.parse import quote

import aiohttp

from app.core import hm_merge, hm_parse

log = logging.getLogger("nerkhcar.hm")
BASE = "https://www.hamrah-mechanic.com/carprice/"
BRANDS = ("irankhodro", "saipa", "peugeot")
PAUSE = 2
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept-Language": "fa,en;q=0.8"}
TIMEOUT = aiohttp.ClientTimeout(total=30)


async def _props(session, path: str) -> dict | None:
    """pageProps of one page; None on any failure."""
    try:
        async with session.get(BASE + path) as r:
            if r.status != 200:
                log.warning("hm page failed: %s", r.status)
                return None
            html = await r.text(errors="ignore")
    except Exception as exc:
        log.warning("hm page error: %s", type(exc).__name__)
        return None
    return hm_parse.page_props(html)


async def _brand_rows(session, brand: str, ours: list[str], seen: set) -> list[dict]:
    """Rows of every model of this brand that 1car lacks."""
    props = await _props(session, f"{brand}/")
    if props is None:
        return []
    rows: list[dict] = []
    for slug in hm_merge.missing_slugs(hm_parse.model_slugs(props), ours):
        if slug in seen:
            continue
        seen.add(slug)
        await asyncio.sleep(PAUSE)
        page = await _props(session, f"{brand}/{quote(slug)}/")
        rows += hm_parse.latest_rows(hm_parse.year_rows(page)) if page else []
    return rows


async def fetch_missing_rows(ours: list[str]) -> list[dict]:
    """Rows of models 1car lacks; ours = normalized 1car row names."""
    seen: set[str] = set()
    rows: list[dict] = []
    async with aiohttp.ClientSession(headers=HEADERS, timeout=TIMEOUT) as s:
        for brand in BRANDS:
            rows += await _brand_rows(s, brand, ours, seen)
    return hm_merge.dedupe(rows)
