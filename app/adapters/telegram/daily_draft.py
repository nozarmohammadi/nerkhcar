"""Daily price drafts: glue between the Telegram handler and the database."""
from datetime import datetime
from zoneinfo import ZoneInfo

from app.adapters.telegram import dbrun
from app.config import Settings
from app.data import repo_daily


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
