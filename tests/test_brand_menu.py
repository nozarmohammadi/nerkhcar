"""Tests for the brand group menu and the banner themes."""
from app.adapters.telegram.keyboards import car_price as k
from app.adapters.telegram.texts import car_price as ct
from app.adapters.telegram.texts import daily_prices as t
from app.core import brand_banner, brand_map


def _row(brand, price=100):
    return {"name": "x", "year": 1404, "price_m": price,
            "change_m": 0, "brand": brand}


def _order():
    return tuple(brand_map.names(t.BRAND_GROUPS, t.OTHER_BRAND))


def test_menu_counts_priced_rows_and_skips_empty_groups():
    rows = [_row("پراید"), _row("پراید", None), _row("تویوتا"), _row("ناشناس")]
    assert brand_map.menu(rows, t.BRAND_GROUPS) == [(0, 1), (3, 1), (10, 1)]


def test_split_keeps_original_brands():
    parts = brand_map.split([_row("پراید"), _row("تویوتا")], t.BRAND_GROUPS)
    assert len(parts) == 11 and parts[0][0]["brand"] == "پراید"


def test_other_group_gets_its_own_name():
    rows = [_row("ناشناس"), _row("پراید")]
    out = brand_map.regroup(rows, t.BRAND_GROUPS, t.OTHER_BRAND)
    assert [r["brand"] for r in out] == ["سایپا", t.OTHER_BRAND]


def test_keyboard_callbacks_are_short_and_numeric():
    kb = k.groups_kb([(0, 3), (6, 2)], list(_order()), ct.BTN_GROUP)
    data = [b.callback_data for line in kb.inline_keyboard for b in line]
    assert data == ["cp:g:0", "cp:g:6"]


def test_each_group_has_its_own_theme():
    order = _order()
    assert len({brand_banner.theme_of(n, order) for n in order}) == len(order)
    assert brand_banner.theme_of("?", order) == len(brand_banner.THEMES) - 1


def test_banner_renders_for_every_theme():
    for index in range(len(brand_banner.THEMES)):
        assert brand_banner.render("تویوتا", index)[:4] == b"\x89PNG"


def test_keyboard_two_per_line_with_group_colors():
    items = [(0, 1), (1, 1), (2, 1), (3, 1)]
    kb = k.groups_kb(items, list(_order()), ct.BTN_GROUP, ct.GROUP_STYLES)
    assert [len(line) for line in kb.inline_keyboard] == [2, 2]
    flat = [b.style for line in kb.inline_keyboard for b in line]
    assert flat == ["primary", "primary", "success", "danger"]
