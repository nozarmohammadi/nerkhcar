"""تست شمارندهٔ سهمیه و روز پاسیفیک."""
from datetime import datetime, timezone

from app.core.usage_day import pacific_day
from app.data import repo_usage


def test_pacific_day_boundary():
    before = datetime(2026, 10, 24, 6, 59, tzinfo=timezone.utc)
    after = datetime(2026, 10, 24, 7, 0, tzinfo=timezone.utc)
    assert pacific_day(before) == "2026-10-23"
    assert pacific_day(after) == "2026-10-24"


def test_counter_increments_per_day(conn):
    assert repo_usage.get_count(conn, "2026-10-24") == 0
    repo_usage.add_request(conn, "2026-10-24")
    repo_usage.add_request(conn, "2026-10-24")
    repo_usage.add_request(conn, "2026-10-25")
    assert repo_usage.get_count(conn, "2026-10-24") == 2
    assert repo_usage.get_count(conn, "2026-10-25") == 1
