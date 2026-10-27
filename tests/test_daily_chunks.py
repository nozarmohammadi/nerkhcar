"""Tests for chunked rich tables: size, title/foot placement, hidden rows."""
from app.adapters.telegram.texts import daily_prices as t
from app.core import daily_text


def _rows(n):
    return [
        {"name": f"car{i}", "year": 1405, "price_m": 100 + i, "change_m": 1.5}
        for i in range(n)
    ]


def test_split_into_chunks():
    parts = daily_text.build_html_chunks(_rows(120), "d", t)
    assert len(parts) == 3
    assert all(p.count("<table") == 1 for p in parts)


def test_title_first_foot_last():
    parts = daily_text.build_html_chunks(_rows(120), "d", t)
    assert t.TBL_TITLE in parts[0] and t.TBL_TITLE not in parts[1]
    assert t.FOOT.strip() in parts[-1] and t.FOOT.strip() not in parts[0]


def test_no_price_row_hidden():
    bad = {"name": "bad", "year": 1405, "price_m": None, "change_m": None}
    html = "".join(daily_text.build_html_chunks(_rows(3) + [bad], "d", t))
    assert "bad" not in html


def test_last_column_centered():
    html = daily_text.build_html_chunks(_rows(1), "d", t)[0]
    assert html.count('align="center"') == 2
