"""Tests for keeping only the newest year per trim."""
from app.core import hm_parse


def test_latest_keeps_newest_year_per_name():
    rows = [
        {"name": "a", "year": 1399, "price_m": 1},
        {"name": "b", "year": 1390, "price_m": 2},
        {"name": "a", "year": 1400, "price_m": 3},
    ]
    out = hm_parse.latest_rows(rows)
    assert [(r["name"], r["year"]) for r in out] == [("a", 1400), ("b", 1390)]


def test_latest_empty():
    assert hm_parse.latest_rows([]) == []
