"""Tests for the daily price table image."""
from io import BytesIO

from PIL import Image, features

from app.adapters.telegram.texts import daily_prices as t
from app.core import daily_image, daily_text

NAME = "\u067e\u0698\u0648 207"
ROWS = [
    {"name": NAME, "year": 1405, "price_m": 4020, "change_m": 230},
    {"name": "Tara V4", "year": 1405, "price_m": 4195, "change_m": 0},
    {"name": "Rana", "year": 1405, "price_m": 2375, "change_m": -80},
]


def _size(rows):
    png = daily_image.render(rows, "d", t)
    return Image.open(BytesIO(png)).size


def test_raqm_available():
    assert features.check("raqm")


def test_table_rows_directions():
    cells = daily_text.table_rows(ROWS, t)
    assert [c[3] for c in cells] == [1, 0, -1]
    assert cells[1][2] == t.NO_VALUE
    assert "\u2212" in cells[2][2]


def test_render_size_and_format():
    width, height = _size(ROWS)
    assert width == daily_image.WIDTH and height == daily_image.MIN_HEIGHT


def test_render_grows_with_many_rows():
    assert _size(ROWS * 10)[1] > daily_image.MIN_HEIGHT
