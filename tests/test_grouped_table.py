"""Tests for the brand-grouped rich table."""
from app.adapters.telegram.texts import daily_prices as t
from app.core import daily_text


def _r(brand, n):
    return [
        {"name": f"{brand}{i}", "year": 1404, "price_m": 100 + i,
         "change_m": 1, "brand": brand}
        for i in range(n)
    ]


def _html(rows):
    return daily_text.build_html_chunks(rows, "d", t)


def test_brand_heading_rows():
    html = _html(_r("الف", 2) + _r("ب", 1))[0]
    assert "<td><b>الف</b></td>" in html and "<td><b>ب</b></td>" in html


def test_other_heading_for_rows_without_brand():
    html = _html(_r("الف", 1) + _r("", 1))[0]
    assert f"<td><b>{t.OTHER_BRAND}</b></td>" in html


def test_brand_never_split_across_messages():
    parts = _html(_r("الف", 40) + _r("ب", 40) + _r("ج", 5))
    assert len(parts) == 2
    assert "ب39" in parts[1] and "<td><b>ج</b></td>" in parts[1]
    assert "ب0" not in parts[0] and "الف39" in parts[0]


def test_no_brand_info_stays_flat():
    rows = [{"name": "a", "year": 1404, "price_m": 100, "change_m": 1}]
    assert "<td><b>" not in _html(rows)[0]
