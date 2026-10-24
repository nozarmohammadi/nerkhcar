"""اتصال به SQLite و اجرای migrationها (با بکاپ قبل از تغییر)."""
import sqlite3
from datetime import datetime
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _applied(conn: sqlite3.Connection) -> set[str]:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        "version TEXT PRIMARY KEY, "
        "applied_at TEXT NOT NULL DEFAULT (datetime('now')))"
    )
    return {r[0] for r in conn.execute("SELECT version FROM schema_migrations")}


def _backup(conn: sqlite3.Connection, backup_dir: Path) -> None:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    dest = sqlite3.connect(backup_dir / f"pre-migrate.{stamp}.db")
    conn.backup(dest)
    dest.close()


def migrate(db_path: Path, backup_dir: Path) -> list[str]:
    conn = connect(db_path)
    done = _applied(conn)
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    pending = [f for f in files if f.stem not in done]
    if pending and done:
        _backup(conn, backup_dir)
    for f in pending:
        conn.executescript(f.read_text(encoding="utf-8"))
        conn.execute("INSERT INTO schema_migrations(version) VALUES (?)", (f.stem,))
        conn.commit()
    conn.close()
    db_path.chmod(0o600)
    return [f.stem for f in pending]
