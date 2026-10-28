"""Display filter: cars with an old newest year are not shown."""
from app.core import brand_groups


def _row(name, year, brand="B"):
    return {"name": name, "year": year, "price_m": 1000, "brand": brand}


def _names(rows, current=1405):
    parts = brand_groups.grouped(rows, current_year=current)
    return [r["name"] for _, part in parts for r in part]


def test_discontinued_model_hidden():
    rows = [_row("Pride", 1397), _row("Pride", 1396), _row("Tara", 1405)]
    assert _names(rows) == ["Tara"]


def test_last_year_kept():
    assert _names([_row("Tara", 1404)]) == ["Tara"]


def test_two_years_old_hidden():
    assert _names([_row("Tara", 1403)]) == []


def test_gregorian_year_converted():
    rows = [_row("Import A", 2025), _row("Import B", 2022)]
    assert _names(rows) == ["Import A"]


def test_only_newest_year_per_name():
    rows = [_row("Tara", 1404), _row("Tara", 1405)]
    assert _names(rows) == ["Tara"]


def test_row_without_year_kept():
    assert _names([_row("Unknown", None)]) == ["Unknown"]
