"""تست پر کردن ستون نام برای پهن‌تر شدن جدول."""
from app.adapters.telegram.texts import daily_prices as t
from app.core import daily_text


def test_name_column_is_padded_for_width():
    rows = [{"name": "x", "year": 1405, "price_m": 1, "change_m": 0, "flags": []}]
    html = daily_text.build_html(rows, "d", t)
    assert "&nbsp;" * 10 in html
