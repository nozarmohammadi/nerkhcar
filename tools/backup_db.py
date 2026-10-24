"""بکاپ روزانهٔ دیتابیس؛ فقط ۷ بکاپ آخر نگه داشته می‌شود."""
import sqlite3
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DB = BASE / "data" / "nerkhcar.db"
OUT = BASE / "backups"
KEEP = 7


def make_backup() -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest_path = OUT / f"daily.{stamp}.db"
    src = sqlite3.connect(DB)
    dest = sqlite3.connect(dest_path)
    src.backup(dest)
    dest.close()
    src.close()
    dest_path.chmod(0o600)
    return dest_path


def prune() -> None:
    files = sorted(OUT.glob("daily.*.db"))
    for old in files[:-KEEP]:
        old.unlink()


if __name__ == "__main__":
    print("بکاپ:", make_backup())
    prune()
