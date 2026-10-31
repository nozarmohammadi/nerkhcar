"""بکاپ روزانهٔ دیتابیس؛ فقط ۷ بکاپ آخر نگه داشته می‌شود."""
import sqlite3
import time
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


# Manual backups (pre-migrate etc.): keep newest MANUAL_KEEP_MIN files,
# delete older ones only if also older than MANUAL_KEEP_DAYS.
MANUAL_KEEP_DAYS = 14
MANUAL_KEEP_MIN = 10
MANUAL_PATTERNS = ("nerkhcar*.db", "nerkhcar.db.*", "pre-*.db")


def prune_manual(out=OUT, now=None, days=MANUAL_KEEP_DAYS, keep_min=MANUAL_KEEP_MIN):
    now = time.time() if now is None else now
    found = set()
    for pat in MANUAL_PATTERNS:
        for p in Path(out).glob(pat):
            if p.is_file() and not p.name.startswith("daily."):
                found.add(p)
    newest_first = sorted(found, key=lambda p: p.stat().st_mtime, reverse=True)
    removed = []
    for p in newest_first[keep_min:]:
        if now - p.stat().st_mtime > days * 86400:
            p.unlink()
            removed.append(p)
    return removed


if __name__ == "__main__":
    print("بکاپ:", make_backup())
    prune()
    print("پاک‌شده از دستی:", [p.name for p in prune_manual()])
