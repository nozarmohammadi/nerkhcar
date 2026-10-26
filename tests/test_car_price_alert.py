from datetime import datetime

from app.core import car_price_alert as a

SAT_10 = datetime(2026, 10, 24, 10, 0)
SAT_19 = datetime(2026, 10, 24, 19, 0)
FRI_19 = datetime(2026, 10, 23, 19, 0)
DAY = "1405-08-02"


def test_nothing_normal():
    assert a.alert_kind(SAT_10, DAY, False, 0, set()) is None


def test_fail_after_three():
    assert a.alert_kind(SAT_10, DAY, False, 3, set()) == "fail"


def test_two_fails_not_enough():
    assert a.alert_kind(SAT_10, DAY, False, 2, set()) is None


def test_fail_once_per_day():
    assert a.alert_kind(SAT_10, DAY, False, 5, {(DAY, "fail")}) is None


def test_late_when_not_saved():
    assert a.alert_kind(SAT_19, DAY, False, 0, set()) == "late"


def test_no_late_when_saved():
    assert a.alert_kind(SAT_19, DAY, True, 0, set()) is None


def test_no_late_on_friday():
    assert a.alert_kind(FRI_19, DAY, False, 0, set()) is None


def test_late_once_per_day():
    assert a.alert_kind(SAT_19, DAY, False, 0, {(DAY, "late")}) is None
