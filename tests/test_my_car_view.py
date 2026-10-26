from app.adapters.telegram.texts import my_car as t
from app.core import my_car_view as v

RES = {"status": "ok", "warn_above_zero": False,
       "quick_sale": (900.0, 950.0), "fair": (950.0, 1050.0),
       "listing": (1050.0, 1100.0)}


def test_round():
    assert v.round_m(1052) == 1050
    assert v.round_m(953.4) == 953


def test_text_has_bands_and_disclaimer():
    text = v.build_text(RES, "آریسان 2", 1404, t)
    assert t.BAND_QUICK in text and t.BAND_FAIR in text
    assert t.BAND_LISTING in text and text.endswith(t.DISCLAIMER)
    assert t.WARN_ZERO not in text


def test_warning_shown():
    text = v.build_text(dict(RES, warn_above_zero=True), "x", 1404, t)
    assert t.WARN_ZERO in text


def test_no_forbidden_claims():
    text = v.build_text(RES, "x", 1404, t)
    assert "٪" not in text and "%" not in text
