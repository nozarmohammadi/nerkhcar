from app.core import car_price_publish as pub


def _row(name, year, market):
    price = f"<span class='price-range'><span>{market}</span></span>"
    cells = [f"<a href='/ci-1'>{name}</a>", str(year), price, "—", "—", "—"]
    return "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"


def test_only_jalali_year_rows():
    html = _row("پراید", 1404, "300,000,000") + _row("وارداتی", 2025, "5,000,000,000")
    assert [r["name"] for r in pub.auto_rows(html)] == ["پراید"]


def test_both_jalali_years_are_kept():
    html = _row("الف", 1404, "300,000,000") + _row("ب", 1405, "400,000,000")
    assert [r["year"] for r in pub.auto_rows(html)] == [1404, 1405]
