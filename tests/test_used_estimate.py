from datetime import datetime, timedelta

import pytest

from app.core.used_estimate import Base, Car, estimate

NOW = datetime(2026, 10, 25, 12, 0)


def _base(hours=1, samples=3, **kw):
    return Base(1000, samples, NOW - timedelta(hours=hours), **kw)


def _run(car, base=None, zero=None):
    return estimate(car, base or _base(), zero, NOW)


@pytest.mark.parametrize("year,km,body,chassis,expected", [
    (1400, 100000, "clean", "healthy", 1000),
    (1400, 60000, "clean", "healthy", 1016),
    (1400, 150000, "clean", "healthy", 940),
    (1395, 200000, "spots_1_2", "healthy", 950),
    (1395, 350000, "repaint_or_replaced", "healthy", 702),
    (1397, 160000, "spots_1_2", "minor_fixed", 877.5),
    (1393, 800000, "repaint_or_replaced", "major", 550),
    (1400, 100000, "unknown", "unknown", 897),
    (1405, 3000, "clean", "healthy", 1020),
])
def test_central_price(year, km, body, chassis, expected):
    res = _run(Car(year, km, body, chassis))
    assert res["status"] == "ok"
    assert res["central"] == pytest.approx(expected)


def test_fair_band_normal():
    res = _run(Car(1400, 100000, "clean", "healthy"))
    assert res["fair"] == pytest.approx((980, 1020))


def test_fair_band_unknown_answers_double_spread():
    res = _run(Car(1400, 100000, "unknown", "unknown"))
    assert res["fair"] == pytest.approx((897 * 0.96, 897 * 1.04))


def test_stale_data_widens_band():
    res = estimate(Car(1400, 100000, "clean", "healthy"), _base(48), None, NOW)
    assert res["fair"] == pytest.approx((970, 1030))


def test_too_old_base_is_insufficient():
    res = estimate(Car(1400, 100000, "clean", "healthy"), _base(80), None, NOW)
    assert res["status"] == "insufficient"


def test_few_samples_is_insufficient():
    res = _run(Car(1400, 100000, "clean", "healthy"), _base(samples=2))
    assert res["status"] == "insufficient"


def test_missing_base_is_insufficient():
    res = estimate(Car(1400, 1, "clean", "healthy"), None, None, NOW)
    assert res["status"] == "insufficient"


def test_negative_km_is_invalid():
    assert _run(Car(1400, -1, "clean", "healthy"))["status"] == "invalid"


def test_warn_above_zero_for_young_car():
    res = _run(Car(1402, 60000, "clean", "healthy"), zero=900)
    assert res["warn_above_zero"] is True
    assert res["fair"] == pytest.approx((970, 1030))


def test_no_warn_for_old_car_or_without_zero():
    old = _run(Car(1395, 200000, "clean", "healthy"), zero=500)
    assert old["warn_above_zero"] is False
    young = _run(Car(1402, 60000, "clean", "healthy"))
    assert young["warn_above_zero"] is False


def test_illiquid_and_fallback_double_spread():
    car = Car(1400, 100000, "clean", "healthy")
    assert _run(car, _base(liquidity="C"))["fair"] == pytest.approx((960, 1040))
    assert _run(car, _base(is_fallback=True))["fair"] == pytest.approx((960, 1040))
