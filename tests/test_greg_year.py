"""Tests for Gregorian years of imported cars."""
from app.core import my_car_input, my_car_years

ROWS = [
    {"name": "benz", "year": 2024, "price_m": 9000},
    {"name": "benz", "year": 2022, "price_m": 7000},
    {"name": "pride", "year": 1403, "price_m": 500},
]


def test_read_year_accepts_both_calendars():
    assert my_car_input.read_year("2020", 1405) == 2020
    assert my_car_input.read_year("1402", 1405) == 1402
    assert my_car_input.read_year("2100", 1405) is None
    assert my_car_input.read_year("1406", 1405) is None


def test_match_year_follows_table_calendar():
    assert my_car_years.match_year(ROWS, "benz", 1401) == 2022
    assert my_car_years.match_year(ROWS, "benz", 2021) == 2021
    assert my_car_years.match_year(ROWS, "pride", 2023) == 1402
    assert my_car_years.match_year(ROWS, "none", 2023) == 2023


def test_check_year_with_gregorian_rows():
    assert my_car_years.check_year(ROWS, "benz", 2020) == "ok"
    assert my_car_years.check_year(ROWS, "benz", 1405) == "after_last"
    assert my_car_years.check_year(ROWS, "none", 2020) == "unknown_model"


def test_to_jalali():
    assert my_car_years.to_jalali(2020) == 1399
    assert my_car_years.to_jalali(1399) == 1399
