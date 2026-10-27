"""Tests for grouping rows by brand."""
from app.core import brand_groups as bg


def _r(brand):
    return {"name": "x", "year": 1404, "price_m": 100, "brand": brand}


def test_has_brands():
    assert bg.has_brands([_r("الف")])
    assert not bg.has_brands([_r(""), {"name": "z"}])


def test_grouped_order_and_other_last():
    rows = [_r("الف"), _r(""), _r("ب"), _r("الف"), _r(None)]
    got = [(b, len(g)) for b, g in bg.grouped(rows)]
    assert got == [("الف", 2), ("ب", 1), ("", 2)]


def test_no_brand_info_is_one_plain_group():
    rows = [_r(""), {"name": "z", "price_m": 1}]
    assert bg.grouped(rows) == [(None, rows)]
