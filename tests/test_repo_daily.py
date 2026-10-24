"""Tests for repo_daily (real SQLite in a temp folder, no network)."""
import sqlite3

import pytest

from app.data import db, repo_daily

ROWS = [{"name": "سهند", "year": 1405, "price_m": 1810, "change_m": 5.0, "flags": []}]
DAY = "2026-10-24"


def _open(tmp_path):
    path = tmp_path / "t.db"
    applied = db.migrate(path, tmp_path / "bk")
    return path, applied


def test_migration_creates_table(tmp_path):
    path, applied = _open(tmp_path)
    assert "003_daily_batches" in applied
    conn = sqlite3.connect(path)
    names = [r[0] for r in conn.execute("SELECT name FROM sqlite_master")]
    assert "daily_batches" in names


def test_no_draft_returns_none(tmp_path):
    path, _ = _open(tmp_path)
    assert repo_daily.find_draft(sqlite3.connect(path), 1, DAY) is None


def test_rows_survive_reopen(tmp_path):
    path, _ = _open(tmp_path)
    conn = sqlite3.connect(path)
    batch = repo_daily.create_draft(conn, 1, DAY)
    repo_daily.save_rows(conn, batch, ROWS, 2)
    conn.close()
    again = repo_daily.find_draft(sqlite3.connect(path), 1, DAY)
    assert again == {"id": batch, "photos": 2, "rows": ROWS}


def test_other_admin_or_day_not_found(tmp_path):
    path, _ = _open(tmp_path)
    conn = sqlite3.connect(path)
    repo_daily.create_draft(conn, 1, DAY)
    assert repo_daily.find_draft(conn, 2, DAY) is None
    assert repo_daily.find_draft(conn, 1, "2026-10-25") is None


@pytest.mark.parametrize("status", ["sent", "cancelled"])
def test_closed_batch_is_not_a_draft(tmp_path, status):
    path, _ = _open(tmp_path)
    conn = sqlite3.connect(path)
    batch = repo_daily.create_draft(conn, 1, DAY)
    repo_daily.set_status(conn, batch, status)
    assert repo_daily.find_draft(conn, 1, DAY) is None


def test_bad_status_raises(tmp_path):
    path, _ = _open(tmp_path)
    conn = sqlite3.connect(path)
    batch = repo_daily.create_draft(conn, 1, DAY)
    with pytest.raises(ValueError):
        repo_daily.set_status(conn, batch, "weird")


def test_save_after_sent_is_ignored(tmp_path):
    path, _ = _open(tmp_path)
    conn = sqlite3.connect(path)
    batch = repo_daily.create_draft(conn, 1, DAY)
    repo_daily.set_status(conn, batch, "sent")
    repo_daily.save_rows(conn, batch, ROWS, 5)
    row = conn.execute("SELECT rows_json, photos FROM daily_batches").fetchone()
    assert row == ("[]", 0)
