"""Keep the FX cache fresh in the background (the mini-app only reads it)."""
import asyncio
import logging

from app.adapters.telegram import fx_refresh
from app.config import Settings

log = logging.getLogger("nerkhcar.fx")
# Rows older than 5 minutes are refreshed, so data is never older than ~10 minutes.
INTERVAL = 300


async def run_round(settings: Settings) -> bool:
    """Refresh stale rows once; a failure is logged and never raised."""
    try:
        await fx_refresh.get_rows(settings)
    except Exception as exc:
        log.warning("fx job error: %s", type(exc).__name__)
        return False
    return True


async def loop(settings: Settings) -> None:
    """Run forever: one refresh round every INTERVAL seconds."""
    while True:
        await run_round(settings)
        await asyncio.sleep(INTERVAL)
