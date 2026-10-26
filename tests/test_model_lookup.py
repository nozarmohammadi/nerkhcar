from app.core import model_lookup as m

ROWS = [
    {"name": "B", "year": 1404, "price_m": 1800},
    {"name": "B", "year": 1405, "price_m": 2000},
    {"name": "A", "year": 1405, "price_m": 900},
]


def test_names_sorted_unique():
    assert m.model_names(ROWS) == ["A", "B"]


def test_pages():
    names = [str(i) for i in range(17)]
    assert m.page_count(names) == 3
    assert len(m.page_of(names, 2)) == 1
    assert m.page_of(names, 1)[0] == (8, "8")


def test_years_newest_first():
    assert m.years_of(ROWS, "B") == [1405, 1404]


def test_exact_price():
    assert m.price_for(ROWS, "B", 1404) == (1800, True)


def test_old_year_uses_newest():
    assert m.price_for(ROWS, "B", 1398) == (2000, False)


def test_unknown_model():
    assert m.price_for(ROWS, "Z", 1405) is None
    assert m.newest_price(ROWS, "Z") is None
