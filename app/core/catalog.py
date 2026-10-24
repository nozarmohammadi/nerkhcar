"""منطق کاتالوگ: اعتبارسنجی نام و افزودن برند/مدل/تیپ. بدون تلگرام."""
import sqlite3

from app.data import repo_catalog

MAX_NAME = 40


def clean_name(text: str) -> str | None:
    name = " ".join(text.split())
    if not name or len(name) > MAX_NAME or name.startswith("/"):
        return None
    return name


def _parent_ok(conn: sqlite3.Connection, kind: str, parent_id: int) -> bool:
    if kind == "brand":
        return True
    if kind == "model":
        return repo_catalog.get_brand(conn, parent_id) is not None
    return repo_catalog.get_model(conn, parent_id) is not None


def _insert(conn: sqlite3.Connection, kind: str, parent_id: int, name: str) -> None:
    if kind == "brand":
        repo_catalog.add_brand(conn, name)
    elif kind == "model":
        repo_catalog.add_model(conn, parent_id, name)
    else:
        repo_catalog.add_trim(conn, parent_id, name)


def add_item(conn: sqlite3.Connection, kind: str, parent_id: int, text: str) -> str:
    """نتیجه: ok، exists، bad_name یا no_parent."""
    name = clean_name(text)
    if name is None:
        return "bad_name"
    if not _parent_ok(conn, kind, parent_id):
        return "no_parent"
    try:
        _insert(conn, kind, parent_id, name)
    except sqlite3.IntegrityError:
        return "exists"
    return "ok"
