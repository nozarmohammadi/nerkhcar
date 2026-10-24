"""Tests for daily_draft glue (temp database, no network)."""
from types import SimpleNamespace

from app.adapters.telegram import daily_draft
from app.data import db

ROWS = [{"name": "سهند", "year": 1405, "price_m": 1810, "change_m": 5.0, "flags": []}]


def _settings(tmp_path):
    (tmp_path / "b").mkdir()
    db.migrate(tmp_path / "t.db", tmp_path / "b")
    return SimpleNamespace(db_path=tmp_path / "t.db")


def test_no_draft_at_first(tmp_path):
    assert daily_draft.find_today(_settings(tmp_path), 7) is None


def test_save_then_find(tmp_path):
    s = _settings(tmp_path)
    batch = daily_draft.start(s, 7)
    daily_draft.save(s, batch, ROWS, 2)
    found = daily_draft.find_today(s, 7)
    assert found == {"id": batch, "photos": 2, "rows": ROWS}


def test_closed_is_not_found(tmp_path):
    s = _settings(tmp_path)
    batch = daily_draft.start(s, 7)
    daily_draft.close(s, batch, "sent")
    assert daily_draft.find_today(s, 7) is None


def test_other_admin_does_not_see_it(tmp_path):
    s = _settings(tmp_path)
    daily_draft.start(s, 7)
    assert daily_draft.find_today(s, 8) is None


def test_today_is_iso_date():
    assert len(daily_draft.today()) == 10


def test_save_if_open_writes_rows(tmp_path):
    s = _settings(tmp_path)
    batch = daily_draft.start(s, 7)
    daily_draft.save_if_open(s, {"batch_id": batch}, ROWS, 3)
    assert daily_draft.find_today(s, 7)["photos"] == 3


def test_save_if_open_without_batch_does_nothing(tmp_path):
    s = _settings(tmp_path)
    daily_draft.save_if_open(s, {}, ROWS, 3)
    assert daily_draft.find_today(s, 7) is None


def test_close_if_open_marks_sent(tmp_path):
    s = _settings(tmp_path)
    batch = daily_draft.start(s, 7)
    daily_draft.close_if_open(s, {"batch_id": batch}, "sent")
    assert daily_draft.find_today(s, 7) is None
