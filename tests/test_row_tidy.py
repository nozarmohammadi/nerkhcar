"""Display tidy-up: newest year, families together, change cap and format."""
from app.core import brand_groups as bg, car_price_parse as parse, daily_text


def _row(name, year, brand="b"):
    return {"name": name, "year": year, "brand": brand}


def test_newest_year_only():
    rows = [_row("a x", 1404), _row("a x", 1405), _row("b y", 1401), _row("b y", 1400)]
    out = bg.grouped(rows)[0][1]
    assert [(r["name"], r["year"]) for r in out] == [("a x", 1405), ("b y", 1401)]


def test_family_together():
    rows = [_row("p 207 auto", 1405), _row("p 405", 1405), _row("p 207 manual", 1405)]
    names = [r["name"] for r in bg.grouped(rows)[0][1]]
    assert names == ["p 207 auto", "p 207 manual", "p 405"]


def test_big_daily_change_dropped():
    cell = "<span class='trend-down'>\u25bc 52.9\u066a</span>"
    assert parse._change(cell, 36_000_000_000) is None


def test_small_daily_change_kept():
    cell = "<span class='trend-up'>\u25b2 2.0</span>"
    assert parse._change(cell, 100_000_000) == 1960784


def test_change_format():
    assert daily_text._fmt_change(40433.1) == "40,433.1"
    assert daily_text._fmt_change(1500.0) == "1,500"
