"""Mileage must not change the estimate until it is calibrated."""
from datetime import datetime, timezone

from pytest import approx

from app.core import my_car_calc

NOW = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
DATA = {
    "rows": [{"name": "x", "year": 1400, "price_m": 500}],
    "published_at": "2026-10-28 08:00:00",
}


def _run(km):
    answers = {"name": "x", "year": 1400, "km": km,
               "body": "clean", "chassis": "healthy"}
    return my_car_calc.compute(DATA, answers, NOW)


def test_km_does_not_change_price():
    low, high, none = _run(10000), _run(400000), _run(None)
    assert low["central"] == approx(high["central"])
    assert none["central"] == approx(low["central"])
