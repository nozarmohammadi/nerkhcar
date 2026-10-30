"""Old cars keep losing value after 12 years (the curve must not go flat)."""
from datetime import datetime

from app.core import used_base_auto as ub


def test_curve_keeps_falling_after_twelve_years():
    assert ub.age_factor(16) < ub.age_factor(12)
    assert ub.age_factor(20) < ub.age_factor(16)


def test_old_pride_is_aged_about_twenty_percent():
    now = datetime(2026, 10, 29)
    base = ub.base_aged(871.0, 1394, 1390, now, now)
    assert 690 < base.price < 715
