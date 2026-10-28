"""Tests for the four fixed Tehran slots and the late-alert hour."""
from datetime import datetime
from zoneinfo import ZoneInfo

from app.core import car_price_alert as alerts
from app.core import car_price_schedule as s

TEHRAN = ZoneInfo("Asia/Tehran")
DAY = "1405-08-03"


def _at(hour, minute, sec=0, day=25):
    return datetime(2026, 10, day, hour, minute, sec, tzinfo=TEHRAN)


def test_four_slots_exact():
    assert s.SLOTS == ((11, 30), (12, 30), (13, 30), (14, 30))
    assert s.FINAL == (14, 30)


def test_due_only_inside_grace():
    assert s.due_slot(_at(11, 30)) == (11, 30)
    assert s.due_slot(_at(14, 35)) == (14, 30)
    assert s.due_slot(_at(11, 29, 59)) is None
    assert s.due_slot(_at(11, 41)) is None
    assert s.due_slot(_at(14, 41)) is None


def test_friday_has_no_slot():
    assert s.due_slot(_at(12, 30, day=30)) is None


def test_zone_is_tehran_not_system():
    utc = datetime(2026, 10, 25, 8, 0, tzinfo=ZoneInfo("UTC"))
    assert s.due_slot(utc) == (11, 30)


def test_sleep_never_passes_next_slot():
    assert s.seconds_to_next(_at(11, 29, 50)) == 10
    assert s.seconds_to_next(_at(9, 0)) == s.TICK_SEC
    assert s.seconds_to_next(_at(14, 31)) == s.TICK_SEC


def test_no_jitter_left():
    assert not hasattr(s, "JITTER_MIN")
    assert not hasattr(s, "INTERVAL_MIN")


def test_late_alert_moves_to_fifteen():
    assert alerts.alert_kind(_at(14, 59), DAY, False, 0, set()) is None
    assert alerts.alert_kind(_at(15, 0), DAY, False, 0, set()) == "late"
