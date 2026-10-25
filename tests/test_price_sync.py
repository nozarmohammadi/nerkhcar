import pytest

from app.core import ref_import
from app.data import db, repo_catalog, repo_prices


def _conn(tmp_path):
    path = tmp_path / "t.db"
    db.migrate(path, tmp_path)
    return db.connect(path)


def _row(name, year, price):
    return {"name": name, "year": year, "price_m": price,
            "change_m": None, "flags": []}


def _save(conn, brand_id, rows):
    return ref_import.save_references(conn, rows, brand_id, "src", 1, "پایه")


def _trim_id(conn, name):
    sql = "SELECT t.id FROM trims t JOIN models m ON m.id=t.model_id WHERE m.name=?"
    return conn.execute(sql, (name,)).fetchone()[0]


def test_save_writes_our_price(tmp_path):
    conn = _conn(tmp_path)
    brand = repo_catalog.add_brand(conn, "X")
    _save(conn, brand, [_row("ساینا", 1404, 1750)])
    price = repo_prices.get_price(conn, _trim_id(conn, "ساینا"), 1404)
    assert (price.low, price.high, price.status) == (1750, 1750, "published")


def test_second_save_touches_only_saved_rows(tmp_path):
    conn = _conn(tmp_path)
    brand = repo_catalog.add_brand(conn, "X")
    _save(conn, brand, [_row("ساینا", 1404, 1750), _row("تارا", 1404, 1800)])
    conn.execute("UPDATE prices SET updated_at='2000-01-01 00:00:00'")
    conn.commit()
    _save(conn, brand, [_row("ساینا", 1404, 1760)])
    a = repo_prices.get_price(conn, _trim_id(conn, "ساینا"), 1404)
    b = repo_prices.get_price(conn, _trim_id(conn, "تارا"), 1404)
    assert a.low == 1760 and a.updated_at != "2000-01-01 00:00:00"
    assert b.low == 1800 and b.updated_at == "2000-01-01 00:00:00"


def test_error_leaves_nothing_half_saved(tmp_path, monkeypatch):
    conn = _conn(tmp_path)
    brand = repo_catalog.add_brand(conn, "X")

    def boom(*args, **kwargs):
        raise RuntimeError("fail")

    monkeypatch.setattr(ref_import.repo_audit, "add_entry", boom)
    with pytest.raises(RuntimeError):
        _save(conn, brand, [_row("ساینا", 1404, 1750)])
    for table in ("prices", "reference_prices", "price_history"):
        assert conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0
