from app.core import my_car_years as y

ROWS = [
    {"name": "A", "year": 1403, "price_m": 1},
    {"name": "A", "year": 1402, "price_m": 1},
]


def test_ok_and_older():
    assert y.check_year(ROWS, "A", 1402) == "ok"
    assert y.check_year(ROWS, "A", 1390) == "ok"


def test_after_last():
    assert y.check_year(ROWS, "A", 1404) == "after_last"
    assert y.last_year(ROWS, "A") == 1403


def test_unknown():
    assert y.check_year(ROWS, "Z", 1402) == "unknown_model"
    assert y.last_year(ROWS, "Z") is None
