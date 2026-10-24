"""تست ویرایش پیش‌نویس و ذخیرهٔ مرجع‌ها."""
import pytest

from app.core import ref_import, table_parse
from app.data import repo_audit, repo_catalog, repo_refs

TRIM = "پایه"


def _rows():
    raw = [
        {"name": "ساینا اس", "year": 1405, "price": 1720000000, "change": 15000000},
        {"name": "سهند", "year": 1405, "price": 1810000000, "change": 5000000},
        {"name": "ساینا اتومات", "year": 1405, "price": None, "change": None},
    ]
    return table_parse.normalize_rows(raw)


def _brand(conn):
    return repo_catalog.add_brand(conn, "سایپا")


def _count(conn, table):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_apply_edit_all_fields():
    rows = _rows()
    assert ref_import.apply_edit(rows, 1, "price", "1750") == "ok"
    assert rows[0]["price_m"] == 1750 and rows[0]["flags"] == []
    assert ref_import.apply_edit(rows, 1, "year", "1404") == "ok"
    assert rows[0]["year"] == 1404
    assert ref_import.apply_edit(rows, 2, "name", "سهند اتومات") == "ok"
    assert rows[1]["name"] == "سهند اتومات"
    assert ref_import.apply_edit(rows, 3, "delete", "") == "ok"
    assert len(rows) == 2


def test_apply_edit_errors():
    rows = _rows()
    assert ref_import.apply_edit(rows, 0, "price", "1") == "bad_index"
    assert ref_import.apply_edit(rows, 4, "price", "1") == "bad_index"
    assert ref_import.apply_edit(rows, 1, "price", "abc") == "bad_value"
    assert ref_import.apply_edit(rows, 1, "color", "x") == "bad_field"
    assert len(rows) == 3 and rows[0]["price_m"] == 1720


def test_edit_unblocks_row():
    rows = _rows()
    ready, blocked = ref_import.split_rows(rows)
    assert len(ready) == 2 and len(blocked) == 1
    ref_import.apply_edit(rows, 3, "price", "1900")
    ready, blocked = ref_import.split_rows(rows)
    assert len(ready) == 3 and blocked == []
    ref_import.apply_edit(rows, 3, "price", "5")
    assert "range" in rows[2]["flags"]
    assert len(ref_import.split_rows(rows)[1]) == 1


def test_save_creates_catalog_and_references(conn):
    brand = _brand(conn)
    result = ref_import.save_references(conn, _rows(), brand, "auto_price", 7, TRIM)
    assert result == ("ok", 2, 1)
    names = [m["name"] for m in repo_catalog.list_models(conn, brand)]
    assert sorted(names) == sorted(["ساینا اس", "سهند"])
    refs = conn.execute(
        "SELECT source_name, low, high, year, entered_by "
        "FROM reference_prices ORDER BY id").fetchall()
    assert [tuple(r) for r in refs] == [
        ("auto_price", 1720, 1720, 1405, 7),
        ("auto_price", 1810, 1810, 1405, 7),
    ]
    trims = conn.execute("SELECT name FROM trims").fetchall()
    assert {t["name"] for t in trims} == {TRIM}
    assert repo_audit.recent(conn, 1)[0]["action"] == "refs_imported"


def test_save_twice_reuses_catalog(conn):
    brand = _brand(conn)
    ref_import.save_references(conn, _rows(), brand, "a", 7, TRIM)
    ref_import.save_references(conn, _rows(), brand, "b", 7, TRIM)
    assert len(repo_catalog.list_models(conn, brand)) == 2
    assert _count(conn, "trims") == 2
    assert _count(conn, "reference_prices") == 4


def test_save_unknown_brand_and_nothing_ready(conn):
    assert ref_import.save_references(
        conn, _rows(), 999, "a", 7, TRIM) == ("no_brand", 0, 0)
    brand = _brand(conn)
    blocked_only = table_parse.normalize_rows(
        [{"name": "x", "year": 1405, "price": None}])
    assert ref_import.save_references(
        conn, blocked_only, brand, "a", 7, TRIM) == ("nothing", 0, 1)
    assert _count(conn, "reference_prices") == 0


def test_save_rolls_back_on_error(conn, monkeypatch):
    brand = _brand(conn)

    def boom(*args, **kwargs):
        raise RuntimeError("x")

    monkeypatch.setattr(repo_refs, "add_reference", boom)
    with pytest.raises(RuntimeError):
        ref_import.save_references(conn, _rows(), brand, "a", 7, TRIM)
    assert _count(conn, "models") == 0
