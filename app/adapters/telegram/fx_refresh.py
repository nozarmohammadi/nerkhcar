"""Fresh FX rows for users: refresh from the web at most every few minutes."""
import asyncio
import logging
import sqlite3
from datetime import datetime, timezone

from app.adapters import fx_fetch
from app.adapters.telegram import dbrun
from app.config import Settings
from app.core import fx_parse, fx_view
from app.data import repo_fx

log = logging.getLogger("nerkhcar.fx")
_LOCK = asyncio.Lock()


def _load(settings: Settings) -> list[dict]:
    return dbrun.run(settings, repo_fx.load_rows, fx_parse.WANTED)


def _stale(rows: list[dict]) -> bool:
    now = datetime.now(timezone.utc)
    return fx_view.is_stale(rows, len(fx_parse.WANTED), now)


async def _refresh(settings: Settings) -> None:
    """Download and store new prices; on any failure keep the old ones."""
    parsed = fx_parse.parse_pages(await fx_fetch.fetch_pages())
    if not parsed:
        log.warning("fx refresh got no rows")
        return
    try:
        dbrun.run(
            settings, repo_fx.save_rows,
            {k: v["toman"] for k, v in parsed.items()})
    except sqlite3.Error as exc:
        log.warning("fx save failed: %s", type(exc).__name__)


async def get_rows(settings: Settings) -> list[dict]:
    """Stored rows, refreshed first when missing or older than 5 minutes."""
    rows = _load(settings)
    if not _stale(rows):
        return rows
    async with _LOCK:
        rows = _load(settings)
        if _stale(rows):
            await _refresh(settings)
            rows = _load(settings)
    return rows
