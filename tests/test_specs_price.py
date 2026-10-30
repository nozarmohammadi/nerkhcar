"""Tests: price lookup by name and the buttons under a car's specs."""
from app.adapters.telegram.keyboards import specs as k
from app.core import price_lookup

KOOIK = "\u06a9\u0648\u06cc\u06cc\u06a9"
KOOIK_ARABIC = "\u0643\u0648\u064a\u064a\u0643"
ROWS = [
    {"name": "دنا پلاس", "year": 1403, "price_m": 900},
    {"name": "دنا پلاس", "year": 1404, "price_m": 1000},
    {"name": "رانا LX", "year": 1404, "price_m": None},
    {"name": KOOIK, "year": 1404, "price_m": 500},
]


def _data(kb):
    return [b.callback_data for row in kb.inline_keyboard for b in row]


def test_lookup_picks_newest_year():
    assert price_lookup.lookup(ROWS, "دنا پلاس")["price_m"] == 1000


def test_lookup_ignores_arabic_letters():
    assert price_lookup.lookup(ROWS, KOOIK_ARABIC)["price_m"] == 500


def test_lookup_none_without_price_or_name():
    assert price_lookup.lookup(ROWS, "رانا LX") is None
    assert price_lookup.lookup(ROWS, "ناشناس") is None


def test_detail_kb_with_price():
    assert _data(k.detail_kb(7, 2, True)) == ["spec:p:7", "spec:g:2"]


def test_detail_kb_without_price():
    assert _data(k.detail_kb(7, 2, False)) == ["spec:g:2"]


def test_back_kb():
    assert _data(k.back_kb(3)) == ["spec:g:3"]
