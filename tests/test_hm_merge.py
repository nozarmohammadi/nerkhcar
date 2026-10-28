"""Tests for picking the models 1car lacks."""
from app.core import hm_merge


def _row(name, year):
    return {"name": name, "year": year, "price_m": 1, "change_m": None,
            "brand": "", "flags": []}


def test_missing_slugs_use_normalized_substring():
    models = {"a": "پژو 405", "b": "پژو 207"}
    assert hm_merge.missing_slugs(models, ["پژو 207 صندوقدار"]) == ["a"]


def test_nothing_missing_when_all_present():
    assert hm_merge.missing_slugs({"a": "دنا"}, ["دنا پلاس"]) == []


def test_dedupe_keeps_first_and_order():
    rows = [_row("x", 1), _row("y", 1), _row("x", 1), _row("x", 2)]
    out = hm_merge.dedupe(rows)
    assert [(r["name"], r["year"]) for r in out] == [("x", 1), ("y", 1), ("x", 2)]
