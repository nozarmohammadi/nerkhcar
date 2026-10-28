"""Tests for the base price of the my-car estimate (patch alef)."""
from datetime import datetime, timezone

from pytest import approx

from app.core import my_car_calc

NOW = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
STAMP = "2026-10-28 08:00:00"


def _data(rows, stamp=STAMP):
    return {"rows": rows, "published_at": stamp}


def _ans(year):
    return {"name": "x", "year": year, "km": None,
            "body": "clean", "chassis": "healthy"}


def test_exact_year_is_used_as_is():
    rows = [{"name": "x", "year": 1400, "price_m": 500}]
    res = my_car_calc.compute(_data(rows), _ans(1400), NOW)
    assert res["status"] == "ok"
    assert res["central"] == approx(500)
    assert res["confidence_low"] is False


def test_missing_year_is_aged_from_newest():
    rows = [{"name": "x", "year": 1403, "price_m": 600}]
    res = my_car_calc.compute(_data(rows), _ans(1400), NOW)
    assert res["central"] == approx(600 * 0.65 / 0.78)
    assert res["confidence_low"] is True


def test_current_year_follows_the_date():
    rows = [{"name": "x", "year": 1406, "price_m": 900}]
    now = datetime(2027, 4, 1, 12, 0, tzinfo=timezone.utc)
    res = my_car_calc.compute(_data(rows, "2027-04-01 08:00:00"), _ans(1406), now)
    assert res["status"] == "ok"
