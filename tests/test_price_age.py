from datetime import datetime, timezone

from app.core import price_age

NOW = datetime(2026, 10, 26, 12, 0, 0, tzinfo=timezone.utc)


def test_fresh():
    assert price_age.status("2026-10-26 10:00:00", NOW) == "fresh"


def test_exactly_24h_is_fresh():
    assert price_age.status("2026-10-25 12:00:00", NOW) == "fresh"


def test_old():
    assert price_age.status("2026-10-24 12:00:00", NOW) == "old"


def test_exactly_72h_is_old():
    assert price_age.status("2026-10-23 12:00:00", NOW) == "old"


def test_expired():
    assert price_age.status("2026-10-23 11:59:59", NOW) == "expired"
