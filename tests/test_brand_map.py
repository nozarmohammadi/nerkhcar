"""Tests for merging brands into display groups."""
from app.adapters.telegram.texts import daily_prices as t
from app.core import brand_map, daily_text


def _row(name, brand):
    return {"name": name, "year": 1404, "price_m": 100,
            "change_m": 0, "brand": brand}


def test_groups_and_order():
    rows = [_row("a", "تویوتا"), _row("b", "پژو"), _row("c", "پراید"),
            _row("d", "ناشناس")]
    out = brand_map.regroup(rows, t.BRAND_GROUPS)
    assert [r["brand"] for r in out] == [
        "سایپا", "ایران\u200cخودرو", "ژاپنی", ""]
    assert rows[0]["brand"] == "تویوتا"


def test_rows_without_brand_untouched():
    rows = [{"name": "a", "year": 1404, "price_m": 100, "change_m": 0}]
    assert brand_map.regroup(rows, t.BRAND_GROUPS) is rows


def test_big_group_is_split_into_messages():
    rows = [_row(f"m{i}", "چری") for i in range(120)]
    rows = brand_map.regroup(rows, t.BRAND_GROUPS)
    assert len(daily_text.build_html_chunks(rows, "d", t)) >= 3
