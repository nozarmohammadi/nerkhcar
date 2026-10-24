"""مرجع‌های قیمت و ساخت خودکار کاتالوگ برای ورود از عکس.

commit نمی‌کند؛ فراخوان‌کننده یک‌جا commit یا rollback می‌کند.
"""
import sqlite3


def ensure_model(conn: sqlite3.Connection, brand_id: int, name: str) -> int:
    row = conn.execute(
        "SELECT id FROM models WHERE brand_id=? AND name=?", (brand_id, name)
    ).fetchone()
    if row:
        return row["id"]
    cur = conn.execute(
        "INSERT INTO models(brand_id, name) VALUES (?,?)", (brand_id, name)
    )
    return cur.lastrowid


def ensure_trim(conn: sqlite3.Connection, model_id: int, name: str) -> int:
    row = conn.execute(
        "SELECT id FROM trims WHERE model_id=? AND name=?", (model_id, name)
    ).fetchone()
    if row:
        return row["id"]
    cur = conn.execute(
        "INSERT INTO trims(model_id, name) VALUES (?,?)", (model_id, name)
    )
    return cur.lastrowid


def add_reference(
    conn: sqlite3.Connection, trim_id: int, year: int, source: str,
    low: int, high: int, entered_by: int | None,
) -> int:
    cur = conn.execute(
        "INSERT INTO reference_prices(trim_id, year, source_name, low, high, "
        "entered_by) VALUES (?,?,?,?,?,?)",
        (trim_id, year, source, low, high, entered_by),
    )
    return cur.lastrowid
