from datetime import datetime, timezone

from app.core import my_car_calc as c

NOW = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)
DATA = {
    "rows": [{"name": "A", "year": 1404, "price_m": 1000}],
    "published_at": "2026-10-26 02:00:00",
}
ANS = {"name": "A", "year": 1404, "km": 1, "body": 0, "chassis": 0}


def test_ok_three_bands():
    r = c.compute(DATA, ANS, NOW)
    assert r["status"] == "ok"
    assert r["quick_sale"][1] <= r["fair"][0] <= r["fair"][1] <= r["listing"][0]


def test_no_data():
    assert c.compute(None, ANS, NOW)["status"] == "insufficient"


def test_expired_table():
    old = dict(DATA, published_at="2026-10-20 02:00:00")
    assert c.compute(old, ANS, NOW)["reason"] == "stale"


def test_unknown_model():
    r = c.compute(DATA, dict(ANS, name="Z"), NOW)
    assert r["status"] == "insufficient"


def test_bad_option_index():
    assert c.compute(DATA, dict(ANS, km=99), NOW)["status"] == "insufficient"


def test_old_year_still_estimates():
    r = c.compute(DATA, dict(ANS, year=1395), NOW)
    assert r["status"] in ("ok", "invalid", "insufficient")
