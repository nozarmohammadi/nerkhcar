"""Daily 1car.ir download: poll inside a time window until the page is new."""
import asyncio
import logging
import random
from datetime import datetime
from zoneinfo import ZoneInfo

from app.adapters import car_price_fetch as fetch
from app.core import car_price_parse
from app.core import car_price_schedule as sched

log = logging.getLogger("nerkhcar.carprice")
TEHRAN = ZoneInfo("Asia/Tehran")


def already_saved(today: str) -> bool:
    """True if today's raw page is already on disk."""
    return (fetch.RAW_DIR / f"price-{today}.html").exists()


async def run_once(today: str) -> str:
    """One try. Result: fresh (saved), old (page not updated yet) or fail."""
    html = await fetch.fetch_page()
    if html is None:
        return "fail"
    if car_price_parse.page_date(html) != today:
        return "old"
    fetch.save_raw(html)
    return "fresh"


async def loop() -> None:
    """Run forever; an error in one round never stops the loop."""
    while True:
        try:
            now = datetime.now(TEHRAN)
            today = sched.jalali_day(now)
            if sched.in_window(now) and not already_saved(today):
                log.info("car price poll: %s", await run_once(today))
        except Exception as exc:
            log.warning("car price job error: %s", type(exc).__name__)
        wait = sched.INTERVAL_MIN + random.uniform(-sched.JITTER_MIN, sched.JITTER_MIN)
        await asyncio.sleep(wait * 60)
