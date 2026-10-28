"""Tests for the daily price history."""
import sqlite3
from pathlib import Path

from app.data import repo_price_daily

MIGRATION = Path("app/data/migrations/009_price_daily.sql")


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(MIGRATION.read_text(encoding="utf-8"))
    return conn


def test_record_and_series():
    conn = _conn()
    rows = [{"name": "A", "year": 1403, "price_m": 900}]
    assert repo_price_daily.record(conn, "1405-08-07", rows) == 1
    assert repo_price_daily.series(conn, "A", 1403) == [("1405-08-07", 900)]


def test_same_day_overwrites():
    conn = _conn()
    repo_price_daily.record(conn, "1405-08-07", [{"name": "A", "year": 1403, "price_m": 900}])
    repo_price_daily.record(conn, "1405-08-07", [{"name": "A", "year": 1403, "price_m": 950}])
    assert repo_price_daily.series(conn, "A", 1403) == [("1405-08-07", 950)]


def test_days_accumulate_in_order():
    conn = _conn()
    repo_price_daily.record(conn, "1405-08-08", [{"name": "A", "year": 1403, "price_m": 910}])
    repo_price_daily.record(conn, "1405-08-07", [{"name": "A", "year": 1403, "price_m": 900}])
    days = [d for d, _ in repo_price_daily.series(conn, "A", 1403)]
    assert days == ["1405-08-07", "1405-08-08"]
