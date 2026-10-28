"""Daily 1car.ir download: poll inside a time window until the page is new."""
import asyncio
import logging
import random
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.adapters import car_price_fetch as fetch
from app.adapters import hm_fetch
from app.adapters.telegram.texts import car_price as texts
from app.config import Settings
from app.core import car_price_parse, hm_merge, my_car_input
from app.core import car_price_publish as pub
from app.core import car_price_schedule as sched
from app.core import car_price_alert as alerts
from app.data import db, repo_price_daily, repo_prices_tx, repo_published

log = logging.getLogger("nerkhcar.carprice")
TEHRAN = ZoneInfo("Asia/Tehran")


def already_saved(today: str) -> bool:
    """True if today's raw page is already on disk."""
    return (fetch.RAW_DIR / f"price-{today}.html").exists()


def publish_auto(
    settings: Settings, html: str, moment=None, extra=None, force: bool = False
) -> bool:
    """Publish the page rows unless a photo table of today is already live."""
    rows = pub.auto_rows(html) + hm_merge.valid(extra or [])
    if not rows:
        log.warning("car price page gave no rows")
        return False
    stamp, day = pub.stamp_and_day(moment or datetime.now(timezone.utc))
    conn = db.connect(settings.db_path)
    try:
        for row in rows:
            repo_prices_tx.sync_auto_by_model(
                conn, row["name"], row["year"], row["price_m"]
            )
        repo_price_daily.record(conn, day, rows)
        conn.commit()
        return repo_published.replace_auto(conn, day, rows, stamp, force)
    finally:
        conn.close()


async def publish_full(
    settings: Settings, html: str, moment=None, force: bool = False
) -> bool:
    """Publish the 1car rows plus the models 1car lacks (hamrah-mechanic)."""
    ours = [my_car_input.norm(r["name"]) for r in pub.auto_rows(html)]
    try:
        extra = await hm_fetch.fetch_missing_rows(ours)
    except Exception as exc:
        log.warning("hm extra rows failed: %s", type(exc).__name__)
        extra = []
    return publish_auto(settings, html, moment, extra, force)


async def publish_latest(settings: Settings) -> None:
    """After a restart, publish the newest saved raw page (time = file time)."""
    files = sorted(fetch.RAW_DIR.glob("price-*.html"), key=lambda p: p.stat().st_mtime)
    if not files:
        return
    moment = datetime.fromtimestamp(files[-1].stat().st_mtime, timezone.utc)
    html = files[-1].read_text(encoding="utf-8")
    done = await publish_full(settings, html, moment, force=True)
    log.info("startup publish: %s", "published" if done else "skipped")


async def _extend(settings: Settings, today: str) -> None:
    """Add the missing models after a fresh 1car page; never raises."""
    try:
        path = fetch.RAW_DIR / f"price-{today}.html"
        await publish_full(settings, path.read_text(encoding="utf-8"))
    except Exception as exc:
        log.warning("extend publish failed: %s", type(exc).__name__)


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


ALERTS = {"fail": texts.ALERT_FAIL, "late": texts.ALERT_LATE}


async def _send_alert(settings: Settings, bot, kind: str) -> bool:
    """Tell the owner; a send error never stops the job."""
    if bot is None:
        return False
    try:
        await bot.send_message(settings.owner_id, ALERTS[kind])
    except Exception as exc:
        log.warning("owner alert failed: %s", type(exc).__name__)
        return False
    return True


async def _round(settings: Settings, today: str, now, state: dict) -> None:
    """One poll round; keep the count of failed downloads in a row."""
    if sched.in_window(now) and not already_saved(today):
        result = await run_once(today, lambda h: publish_auto(settings, h))
        if result == "fresh":
            await _extend(settings, today)
        log.info("car price poll: %s", result)
        state["fails"] = state["fails"] + 1 if result == "fail" else 0


async def _alert(settings: Settings, bot, now, today: str, state: dict) -> None:
    """Send an owner alert when needed, at most once per kind per day."""
    kind = alerts.alert_kind(
        now, today, already_saved(today), state["fails"], state["sent"])
    if kind and await _send_alert(settings, bot, kind):
        state["sent"].add((today, kind))


async def loop(settings: Settings, bot=None) -> None:
    """Run forever; an error in one round never stops the loop."""
    try:
        await publish_latest(settings)
    except Exception as exc:
        log.warning("car price startup publish: %s", type(exc).__name__)
    state = {"fails": 0, "sent": set()}
    while True:
        try:
            now = datetime.now(TEHRAN)
            today = sched.jalali_day(now)
            await _round(settings, today, now, state)
            await _alert(settings, bot, now, today, state)
        except Exception as exc:
            log.warning("car price job error: %s", type(exc).__name__)
        wait = sched.INTERVAL_MIN + random.uniform(-sched.JITTER_MIN, sched.JITTER_MIN)
        await asyncio.sleep(wait * 60)
