"""Three-value result text of the 'my car' estimate."""
from app.adapters.telegram.texts import my_car as t
from app.core import daily_text, my_car_view

RESULT = {
    "status": "ok",
    "quick_sale": (10810.0, 11155.0),
    "fair": (11155.0, 11845.0),
    "listing": (11845.0, 12190.0),
}


def _text() -> str:
    return my_car_view.build_text(RESULT, "آئودی A3L", 2025, t)


def _full(million: int) -> str:
    return daily_text.fa(f"{million * 1_000_000:,}")


def test_three_values_in_full_toman():
    text = _text()
    assert _full(10810) in text
    assert _full(11500) in text
    assert _full(12190) in text


def test_labels_and_unit():
    text = _text()
    assert t.BAND_QUICK in text
    assert t.BAND_FAIR in text
    assert t.BAND_LISTING in text
    assert "به تومان است" in text
    assert "میلیون" not in text


def test_old_labels_and_ranges_are_gone():
    text = _text()
    assert "فروش سریع" not in text
    assert " تا " not in text


def test_order_low_mid_high():
    text = _text()
    assert text.index(_full(10810)) < text.index(_full(11500))
    assert text.index(_full(11500)) < text.index(_full(12190))
