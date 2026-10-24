"""Daily price drafts: glue between the Telegram handler and the database."""
import logging
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

from app.adapters.telegram import dbrun
from app.config import Settings
from app.data import repo_daily

log = logging.getLogger("nerkhcar")


def today() -> str:
    return datetime.now(ZoneInfo("Asia/Tehran")).date().isoformat()


def find_today(settings: Settings, admin_id: int) -> dict | None:
    return dbrun.run(settings, repo_daily.find_draft, admin_id, today())


def start(settings: Settings, admin_id: int) -> int:
    return dbrun.run(settings, repo_daily.create_draft, admin_id, today())


def save(settings: Settings, batch_id: int, rows: list, photos: int) -> None:
    dbrun.run(settings, repo_daily.save_rows, batch_id, rows, photos)


def close(settings: Settings, batch_id: int, status: str) -> None:
    dbrun.run(settings, repo_daily.set_status, batch_id, status)


def save_if_open(settings: Settings, data: dict, rows: list, photos: int) -> None:
    """Save rows if this session has a batch id; a DB error must not stop the flow."""
    batch_id = data.get("batch_id")
    if batch_id is None:
        return
    try:
        save(settings, batch_id, rows, photos)
    except sqlite3.Error as exc:
        log.warning("draft save failed: %s", type(exc).__name__)


def close_if_open(settings: Settings, data: dict, status: str) -> None:
    """Close the session batch (sent or cancelled) if there is one."""
    batch_id = data.get("batch_id")
    if batch_id is None:
        return
    try:
        close(settings, batch_id, status)
    except sqlite3.Error as exc:
        log.warning("draft close failed: %s", type(exc).__name__)
