from app.core import my_car_input as i

NAMES = ["آریسان 2", "اطلس دنده ای", "اطلس اتوماتیک", "تیگارد X35"]


def test_search_contains():
    assert i.search(NAMES, "اطلس") == ["اطلس دنده ای", "اطلس اتوماتیک"]


def test_search_unifies_letters():
    assert i.search(NAMES, "آریسان") == ["آریسان 2"]
    assert i.search(["تيگارد"], "تیگارد") == ["تيگارد"]


def test_search_case_and_short():
    assert i.search(NAMES, "x35") == ["تیگارد X35"]
    assert i.search(NAMES, "ا") == []


def test_search_limit():
    assert len(i.search(["اطلس %d" % n for n in range(20)], "اطلس")) == 8


def test_year():
    assert i.read_year("۱۴۰۲", 1405) == 1402
    assert i.read_year("1402", 1405) == 1402
    assert i.read_year("2000", 1405) == 2000
    assert i.read_year("2100", 1405) is None
    assert i.read_year("abc", 1405) is None


def test_km():
    assert i.read_km("65,000") == 65000
    assert i.read_km("۰") == 0
    assert i.read_km("-5") is None
    assert i.read_km("9999999") is None
