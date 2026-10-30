"""Tests for the specs table html and text."""
from app.core import specs_html, specs_view

LABELS = (("a", "LA"), ("b", "LB"), ("c", "LC"))


def test_pairs_skip_empty():
    got = specs_view.pairs({"a": "1", "b": "", "_match": "x"}, LABELS)
    assert got == [("LA", "1")]


def test_html_has_table_and_persian_digits():
    html = specs_html.build_html("T", [("LA", "5 door")], ("H1", "H2"))
    assert "<table bordered striped>" in html
    assert "<th>H1</th>" in html
    assert "۵" in html


def test_html_escapes():
    html = specs_html.build_html("T", [("L", "<b>")], ("H1", "H2"))
    assert "<b>" not in html.split("<td>")[2]


def test_text_fallback():
    text = specs_html.build_text("T", [("LA", "5")])
    assert text.startswith("T") and "LA: ۵" in text and text.endswith("LA: ۵")
