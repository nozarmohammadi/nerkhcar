"""Tests for the pure specs logic."""
from app.core import specs_view

GROUPS = (("A", ("saipa",)), ("B", ("ikco", "peugeot")))


def test_prefix():
    assert specs_view.prefix("saipa-111") == "saipa"
    assert specs_view.prefix("toyota") == "toyota"


def test_split_and_unmapped_last():
    rows = [
        {"slug": "saipa-111"}, {"slug": "peugeot-206"},
        {"slug": "kia-cerato"}, {"slug": "ikco-dena"},
    ]
    parts = specs_view.split(rows, GROUPS)
    assert [len(p) for p in parts] == [1, 2, 1]
    assert parts[2][0]["slug"] == "kia-cerato"


def test_names_has_other_last():
    assert specs_view.names(GROUPS, "other") == ["A", "B", "other"]


def test_render_skips_empty_and_missing():
    labels = (("a", "LA"), ("b", "LB"), ("c", "LC"))
    text = specs_view.render("T", {"a": "1", "b": "", "_match": "x"}, labels, "{label}: {value}")
    assert text == "T\n\nLA: 1"
