"""تنظیمات برنامه. فقط از .env می‌خواند و هیچ رازی را چاپ نمی‌کند."""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True, repr=False)
class Settings:
    bot_token: str
    owner_id: int
    db_path: Path
    log_dir: Path

    def __repr__(self) -> str:
        return f"Settings(owner_id={self.owner_id}, token=<hidden>)"


def load_settings() -> Settings:
    load_dotenv(BASE_DIR / ".env")
    token = os.getenv("BOT_TOKEN", "").strip()
    owner = os.getenv("OWNER_ID", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN در فایل .env تنظیم نشده است")
    if not owner.isdigit():
        raise RuntimeError("OWNER_ID در فایل .env باید عدد باشد")
    return Settings(
        bot_token=token,
        owner_id=int(owner),
        db_path=BASE_DIR / "data" / "nerkhcar.db",
        log_dir=BASE_DIR / "logs",
    )
