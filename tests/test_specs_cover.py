"""Tests for group index and cover html of the specs table."""
from app.core import specs_html, specs_view

GROUPS = (("A", ("saipa",)), ("B", ("ikco", "peugeot")))


def test_group_index():
    assert specs_view.group_index("saipa-111", GROUPS) == 0
    assert specs_view.group_index("peugeot-206", GROUPS) == 1
    assert specs_view.group_index("kia-cerato", GROUPS) == 2


def test_cover_img_only_with_id():
    with_id = specs_html.build_html("T", [("L", "1")], ("H1", "H2"), "bx")
    without = specs_html.build_html("T", [("L", "1")], ("H1", "H2"))
    assert 'tg://photo?id=bx' in with_id
    assert "<img" not in without
