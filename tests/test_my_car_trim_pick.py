"""Tests for picking the trim that has a price for the chosen year."""
from types import SimpleNamespace

from app.adapters.telegram.handlers import my_car_result as res

CATALOG = [
    {"model": "A", "trim_id": 1},
    {"model": "A", "trim_id": 2},
    {"model": "B", "trim_id": 3},
]


def test_picks_trim_that_has_price_for_year(monkeypatch):
    prices = {(2, 1400): SimpleNamespace(low=900)}
    monkeypatch.setattr(
        res.repo_prices, "get_price", lambda conn, trim_id, year: prices.get((trim_id, year))
    )
    answers = {"name": "A", "year": 1400, "trim_id": 1, "catalog": CATALOG}
    trim_id, price = res.best_trim(None, answers)
    assert trim_id == 2
    assert price.low == 900


def test_falls_back_to_stored_trim_without_price(monkeypatch):
    monkeypatch.setattr(res.repo_prices, "get_price", lambda conn, trim_id, year: None)
    answers = {"name": "A", "year": 1400, "trim_id": 1, "catalog": CATALOG}
    assert res.best_trim(None, answers) == (1, None)


def test_ignores_other_models(monkeypatch):
    prices = {(3, 1400): SimpleNamespace(low=500)}
    monkeypatch.setattr(
        res.repo_prices, "get_price", lambda conn, trim_id, year: prices.get((trim_id, year))
    )
    answers = {"name": "A", "year": 1400, "trim_id": 1, "catalog": CATALOG}
    assert res.best_trim(None, answers)[0] == 1
