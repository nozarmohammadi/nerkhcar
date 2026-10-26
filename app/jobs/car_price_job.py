"""Daily 1car.ir download: poll inside a time window until the page is new."""
import asyncio
import logging
import random
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.adapters import car_price_fetch as fetch
from app.config import Settings
from app.core import car_price_parse
from app.core import car_price_publish as pub
from app.core import car_price_schedule as sched
from app.data import db, repo_published

log = logging.getLogger("nerkhcar.carprice")
TEHRAN = ZoneInfo("Asia/Tehran")


def already_saved(today: str) -> bool:
    """True if today's raw page is already on disk."""
    return (fetch.RAW_DIR / f"price-{today}.html").exists()


def publish_auto(settings: Settings, html: str, moment=None) -> bool:
    """Publish the page rows unless a photo table of today is already live."""
    rows = pub.auto_rows(html)
    if not rows:
        log.warning("car price page gave no rows")
        return False
    stamp, day = pub.stamp_and_day(moment or datetime.now(timezone.utc))
    conn = db.connect(settings.db_path)
    try:
        return repo_published.replace_auto(conn, day, rows, stamp)
    finally:
        conn.close()


def publish_latest(settings: Settings) -> None:
    """After a restart, publish the newest saved raw page (time = file time)."""
    files = sorted(fetch.RAW_DIR.glob("price-*.html"), key=lambda p: p.stat().st_mtime)
    if files:
        moment = datetime.fromtimestamp(files[-1].stat().st_mtime, timezone.utc)
        publish_auto(settings, files[-1].read_text(encoding="utf-8"), moment)


async def run_once(today: str, on_fresh=None) -> str:
    """One try. Result: fresh (saved), old (page not updated yet) or fail."""
    html = await fetch.fetch_page()
    if html is None:
        return "fail"
    if car_price_parse.page_date(html) != today:
        return "old"
    fetch.save_raw(html)
    if on_fresh is not None:
        on_fresh(html)
    return "fresh"


async def loop(settings: Settings) -> None:
    """Run forever; an error in one round never stops the loop."""
    try:
        publish_latest(settings)
    except Exception as exc:
        log.warning("car price startup publish: %s", type(exc).__name__)
    while True:
        try:
            now = datetime.now(TEHRAN)
            today = sched.jalali_day(now)
            if sched.in_window(now) and not already_saved(today):
                result = await run_once(today, lambda h: publish_auto(settings, h))
                log.info("car price poll: %s", result)
        except Exception as exc:
            log.warning("car price job error: %s", type(exc).__name__)
        wait = sched.INTERVAL_MIN + random.uniform(-sched.JITTER_MIN, sched.JITTER_MIN)
        await asyncio.sleep(wait * 60)
