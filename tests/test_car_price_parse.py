import pytest

from app.core import car_price_parse as cp

TD = "<td class='price-cell'>{}</td>"


def _rng(*nums):
    glue = "<span class='price-to'>تا</span>"
    inner = glue.join(f"<span>{n}</span>" for n in nums)
    return f"<span class='price-range'>{inner}</span>"


def _row(name, year, market="—", factory="—", trend="—"):
    cells = [f"<a href='/ci-1'>{name}</a>", str(year), market, factory, "—", trend]
    return "<tr>" + "".join(TD.format(c) for c in cells) + "</tr>"


HTML = (
    "<tr><td>عنوان</td></tr>"
    + _row("آرتابان توکا", 1405, _rng("6,250,000,000", "6,500,000,000"))
    + _row("آریسان 2", 1404, _rng("1,880,000,000"),
           trend="<span class='trend-up'>▲ 1.1٪</span>")
    + _row("بدون بازار", 1405, factory=_rng("2,026,000,000"))
    + _row("پراید", 1404, _rng("300,000,000"),
           trend="<span class='trend-down'>▼ 2٪</span>")
    + _row("وارداتی", 2025, _rng("5,000,000,000"))
    + '<script>"dateModified": "1405-08-03"</script>'
)


def test_only_rows_with_market_price():
    names = [r["name"] for r in cp.parse_rows(HTML)]
    assert names == ["آرتابان توکا", "آریسان 2", "پراید", "وارداتی"]


def test_range_uses_midpoint():
    assert cp.parse_rows(HTML)[0]["price"] == 6_375_000_000


def test_up_and_down_change():
    rows = {r["name"]: r for r in cp.parse_rows(HTML)}
    expected = 1_880_000_000 * 0.011 / 1.011
    assert rows["آریسان 2"]["change"] == pytest.approx(expected, abs=1)
    assert rows["پراید"]["change"] < 0
    assert rows["آرتابان توکا"]["change"] is None


def test_to_rows_matches_photo_row_shape():
    rows = {r["name"]: r for r in cp.to_rows(HTML)}
    row = rows["آرتابان توکا"]
    assert (row["year"], row["price_m"], row["flags"]) == (1405, 6375, [])
    assert set(row) == {"name", "year", "price_m", "change_m", "flags", "brand"}


def test_gregorian_year_is_flagged():
    rows = {r["name"]: r for r in cp.to_rows(HTML)}
    assert "greg_year" in rows["وارداتی"]["flags"]


def test_persian_digits_are_read():
    html = _row("تست", "۱۴۰۵", _rng("۱,۸۸۰,۰۰۰,۰۰۰"))
    row = cp.parse_rows(html)[0]
    assert (row["year"], row["price"]) == (1405, 1_880_000_000)


def test_page_date():
    assert cp.page_date(HTML) == "1405-08-03"
    assert cp.page_date("<html></html>") is None
