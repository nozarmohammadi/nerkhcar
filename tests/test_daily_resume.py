"""Tests for the daily-prices resume flow (temp database, fake Telegram objects)."""
import asyncio
import sqlite3
from types import SimpleNamespace

from app.adapters.telegram import daily_draft
from app.adapters.telegram.handlers import daily_resume as r
from app.adapters.telegram.handlers.daily_state import Daily
from app.adapters.telegram.texts import daily_prices as t
from app.core import daily_text
from app.data import db

ROWS = [{"name": "سهند", "year": 1405, "price_m": 1810, "change_m": 5.0, "flags": []}]


class FakeState:
    def __init__(self):
        self.data, self.current = {}, None

    async def get_data(self):
        return dict(self.data)

    async def update_data(self, **kwargs):
        self.data.update(kwargs)

    async def set_state(self, value):
        self.current = value

    async def clear(self):
        self.data, self.current = {}, None


class FakeMsg:
    def __init__(self):
        self.chat = SimpleNamespace(id=1)
        self.sent = []

    async def answer(self, text, **kwargs):
        self.sent.append((text, kwargs))
        return SimpleNamespace(message_id=5)


class FakeCb:
    def __init__(self):
        self.from_user = SimpleNamespace(id=7)
        self.message = FakeMsg()

    async def answer(self, *args, **kwargs):
        return None


def _settings(tmp_path):
    (tmp_path / "b").mkdir()
    db.migrate(tmp_path / "t.db", tmp_path / "b")
    return SimpleNamespace(db_path=tmp_path / "t.db")


def _draft(settings):
    batch = daily_draft.start(settings, 7)
    daily_draft.save(settings, batch, ROWS, 2)
    return batch


def test_entry_without_draft_opens_fresh(tmp_path):
    s, state, cb = _settings(tmp_path), FakeState(), FakeCb()
    asyncio.run(r.entry(cb, state, s))
    assert state.current == Daily.photos
    assert state.data["rows"] == [] and state.data["batch_id"] is not None
    assert cb.message.sent[0][0] == t.ASK_PHOTOS
    assert daily_draft.find_today(s, 7) is not None


def test_entry_with_draft_asks(tmp_path):
    s, state, cb = _settings(tmp_path), FakeState(), FakeCb()
    _draft(s)
    asyncio.run(r.entry(cb, state, s))
    expected = t.RESUME_ASK.format(photos=daily_text.fa(2), rows=daily_text.fa(1))
    assert state.current is None
    assert cb.message.sent[0][0] == expected
    assert "reply_markup" in cb.message.sent[0][1]


def test_resume_restores_rows(tmp_path, monkeypatch):
    monkeypatch.setattr(r, "active_admin", lambda s, uid: object())
    s, state, cb = _settings(tmp_path), FakeState(), FakeCb()
    batch = _draft(s)
    asyncio.run(r.on_resume(cb, state, s))
    assert state.current == Daily.photos
    assert state.data == {"rows": ROWS, "photos": 2, "batch_id": batch}


def test_fresh_cancels_old_draft(tmp_path, monkeypatch):
    monkeypatch.setattr(r, "active_admin", lambda s, uid: object())
    s, state, cb = _settings(tmp_path), FakeState(), FakeCb()
    old = _draft(s)
    asyncio.run(r.on_fresh(cb, state, s))
    assert state.data["rows"] == [] and state.data["batch_id"] != old
    conn = sqlite3.connect(s.db_path)
    row = conn.execute("SELECT status FROM daily_batches WHERE id=?", (old,)).fetchone()
    assert row[0] == "cancelled"


def test_non_admin_is_ignored(tmp_path, monkeypatch):
    monkeypatch.setattr(r, "active_admin", lambda s, uid: None)
    s, state, cb = _settings(tmp_path), FakeState(), FakeCb()
    _draft(s)
    asyncio.run(r.on_resume(cb, state, s))
    assert state.current is None and cb.message.sent == []
    assert daily_draft.find_today(s, 7) is not None
