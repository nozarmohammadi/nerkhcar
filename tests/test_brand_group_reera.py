"""The Reera brand belongs to the Iran Khodro group, not the Chinese one."""
from app.adapters.telegram.texts import daily_prices as dp
from app.core import brand_map

REERA = "\u0631\u06cc \u0631\u0627"  # brand name of the Reera crossover
REERA_ZWNJ = "\u0631\u06cc\u200c\u0631\u0627"  # same name with a half-space
IRAN_KHODRO, CHINESE = 1, 2  # group indexes in BRAND_GROUPS


def _row(brand):
    return {"name": "x", "year": 1405, "price_m": 1, "brand": brand}


def test_reera_goes_to_iran_khodro():
    parts = brand_map.split([_row(REERA)], dp.BRAND_GROUPS)
    assert len(parts[IRAN_KHODRO]) == 1
    assert parts[CHINESE] == []


def test_reera_with_half_space_goes_to_iran_khodro():
    parts = brand_map.split([_row(REERA_ZWNJ)], dp.BRAND_GROUPS)
    assert len(parts[IRAN_KHODRO]) == 1
    assert parts[CHINESE] == []
