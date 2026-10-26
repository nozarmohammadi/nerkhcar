from datetime import datetime, timezone

from app.core import used_base_auto as u

NOW = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)
PUB = datetime(2026, 10, 26, 2, 0, tzinfo=timezone.utc)


def test_current_year():
    assert u.current_year(NOW) == 1405


def test_age_zero_and_one():
    assert u.age_factor(0) == 1.00
    assert u.age_factor(1) == 0.97


def test_interpolation():
    assert abs(u.age_factor(4) - 0.855) < 1e-9


def test_old_car_floor():
    assert u.age_factor(30) == 0.55


def test_negative_age_is_zero():
    assert u.age_factor(-2) == 1.00


def test_base_fields():
    b = u.base_from_daily(2000, 1403, PUB, NOW)
    assert abs(b.price - 2000 * 0.93) < 1e-6
    assert b.is_fallback and b.samples == 3
    assert b.updated_at == PUB
