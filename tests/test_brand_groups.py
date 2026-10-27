"""Tests for brand grouping and the brand keyboard."""
from app.adapters.telegram.keyboards import car_price as kb
from app.core import brand_groups as bg


def _r(brand, name="x"):
    return {"name": name, "year": 1404, "price_m": 100, "brand": brand}


ROWS = [_r("الف"), _r("الف"), _r("ب"), _r(""), _r(None)]


def test_has_brands():
    assert bg.has_brands(ROWS)
    assert not bg.has_brands([_r(""), {"name": "z"}])


def test_brand_list_order_and_other_last():
    assert bg.brand_list(ROWS) == [("الف", 2), ("ب", 1), ("", 2)]


def test_rows_of_by_index():
    assert len(bg.rows_of(ROWS, 0)) == 2
    assert [r["brand"] for r in bg.rows_of(ROWS, 1)] == ["ب"]
    assert len(bg.rows_of(ROWS, 2)) == 2
    assert bg.rows_of(ROWS, 3) == []


def test_many_brands_fold_into_other():
    rows = [_r(f"b{i}") for i in range(120)]
    items = bg.brand_list(rows)
    assert len(items) == bg.MAX_BRANDS + 1
    assert items[-1] == ("", 120 - bg.MAX_BRANDS)
    buttons = sum(len(r) for r in kb.brands_kb(items).inline_keyboard)
    assert buttons <= 99


def test_keyboard_callbacks_and_back():
    markup = kb.brands_kb(bg.brand_list(ROWS))
    data = [b.callback_data for row in markup.inline_keyboard for b in row]
    assert data == ["cp:b:0", "cp:b:1", "cp:b:2"]
    assert kb.back_kb().inline_keyboard[0][0].callback_data == "cp:back"
