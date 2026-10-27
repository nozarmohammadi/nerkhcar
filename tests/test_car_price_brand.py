"""Tests that each parsed row carries the brand of its section heading."""
from app.core import car_price_parse


def _row(name, price):
    return (
        '<tr class="price-range"><td>%s</td><td>1404</td><td>%s</td>'
        "<td>0</td><td>0</td><td>2</td></tr>" % (name, price)
    )


HTML = (
    "<h2>قیمت آریسان</h2><table>" + _row("آریسان ۶", "1,000,000,000")
    + "</table><h3>قیمت بی ام و (BMW)</h3><table>"
    + _row("X5", "5,000,000,000") + "</table>"
    + "<h2>سوالات متداول</h2><table>" + _row("X6", "6,000,000,000")
    + "</table>"
)


def test_brand_from_heading():
    rows = car_price_parse.parse_rows(HTML)
    assert [r["brand"] for r in rows] == [
        "آریسان", "بی ام و (BMW)", "بی ام و (BMW)"]


def test_other_heading_keeps_brand():
    rows = car_price_parse.parse_rows(HTML)
    assert rows[2]["name"] == "X6"
    assert rows[2]["brand"] == "بی ام و (BMW)"


def test_to_rows_keeps_brand():
    rows = car_price_parse.to_rows(HTML)
    assert [r["brand"] for r in rows][0] == "آریسان"


def test_row_before_any_heading_has_empty_brand():
    rows = car_price_parse.parse_rows(_row("Z", "2,000,000,000"))
    assert rows[0]["brand"] == ""
