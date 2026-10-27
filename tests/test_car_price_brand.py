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


HEAD_IN_ROW = (
    '<table><tr><td colspan="6"><h2>قیمت آریسان</h2></td></tr>'
    "<tr><td>نام خودرو</td><td>سال ساخت</td></tr>"
    + _row("آریسان ۶", "1,000,000,000")
    + '<tr><td colspan="6"><h2>قیمت پراید</h2></td></tr>'
    + _row("۱۱۱", "300,000,000") + "</table>"
)


def test_heading_inside_table_row():
    rows = car_price_parse.parse_rows(HEAD_IN_ROW)
    assert [r["brand"] for r in rows] == ["آریسان", "پراید"]


def test_arabic_yeh_in_price_word():
    html = "<h2>قيمت تارا</h2>" + _row("تارا", "1,200,000,000")
    assert car_price_parse.parse_rows(html)[0]["brand"] == "تارا"
