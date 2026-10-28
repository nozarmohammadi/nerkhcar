"""Group button counts must equal the rows the table really shows."""
from app.core import brand_map

GROUPS = (("Group A", ("brandA",)), ("Group B", ("brandB",)))


def _row(name, year, brand, price=1000):
    return {"name": name, "year": year, "price_m": price, "brand": brand}


def test_menu_counts_only_visible_rows():
    rows = [
        _row("Pride", 1397, "brandA"),  # discontinued: hidden
        _row("Pride", 1396, "brandA"),  # older year of a hidden model
        _row("Tara", 1405, "brandA"),
        _row("Tara", 1404, "brandA"),  # older year: hidden
        _row("Dena", 1405, "brandB"),
    ]
    assert brand_map.menu(rows, GROUPS, current_year=1405) == [(0, 1), (1, 1)]


def test_menu_drops_group_with_only_old_models():
    rows = [_row("Pride", 1397, "brandA"), _row("Dena", 1405, "brandB")]
    assert brand_map.menu(rows, GROUPS, current_year=1405) == [(1, 1)]


def test_menu_unmapped_brand_counted_last():
    rows = [_row("Zed", 1405, "other")]
    assert brand_map.menu(rows, GROUPS, current_year=1405) == [(2, 1)]
