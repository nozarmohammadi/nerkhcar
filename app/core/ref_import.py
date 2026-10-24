"""ویرایش پیش‌نویس جدول و ذخیرهٔ مرجع‌های قیمت. بدون تلگرام."""
import sqlite3

from app.core import table_parse
from app.data import repo_audit, repo_catalog, repo_refs

BLOCKING = {"no_name", "no_year", "no_price", "bad_year", "range", "bad_row"}


def _recheck(row: dict) -> dict:
    price, change = row["price_m"], row["change_m"]
    million = table_parse.MILLION
    raw = {
        "name": row["name"],
        "year": row["year"],
        "price": None if price is None else price * million,
        "change": None if change is None else change * million,
    }
    return table_parse.normalize_row(raw)


def apply_edit(rows: list[dict], number: int, field: str, value: str) -> str:
    """نتیجه: ok، bad_index، bad_field یا bad_value."""
    if not 1 <= number <= len(rows):
        return "bad_index"
    if field == "delete":
        del rows[number - 1]
        return "ok"
    row = rows[number - 1]
    if field == "name":
        row["name"] = value
    elif field in ("year", "price"):
        num = table_parse.to_int(value)
        if num is None:
            return "bad_value"
        row["year" if field == "year" else "price_m"] = num
    else:
        return "bad_field"
    row.update(_recheck(row))
    return "ok"


def split_rows(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    ready, blocked = [], []
    for row in rows:
        (blocked if BLOCKING & set(row["flags"]) else ready).append(row)
    return ready, blocked


def _save_one(
    conn: sqlite3.Connection, row: dict, brand_id: int, source: str,
    admin_id: int, trim_name: str,
) -> None:
    model_id = repo_refs.ensure_model(conn, brand_id, row["name"])
    trim_id = repo_refs.ensure_trim(conn, model_id, trim_name)
    price = row["price_m"]
    repo_refs.add_reference(conn, trim_id, row["year"], source, price, price, admin_id)


def save_references(
    conn: sqlite3.Connection, rows: list[dict], brand_id: int, source: str,
    admin_id: int, trim_name: str,
) -> tuple[str, int, int]:
    """نتیجه: (وضعیت، تعداد ذخیره‌شده، تعداد ردشده). وضعیت: ok، no_brand، nothing."""
    if repo_catalog.get_brand(conn, brand_id) is None:
        return "no_brand", 0, 0
    ready, blocked = split_rows(rows)
    if not ready:
        return "nothing", 0, len(blocked)
    try:
        for row in ready:
            _save_one(conn, row, brand_id, source, admin_id, trim_name)
        detail = f"n={len(ready)} brand={brand_id}"
        repo_audit.add_entry(conn, admin_id, "refs_imported", detail)
    except Exception:
        conn.rollback()
        raise
    return "ok", len(ready), len(blocked)
