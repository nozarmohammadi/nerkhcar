"""تست پنل مدیریت ادمین‌ها با پیام‌های ساختگی."""
import asyncio
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from app.adapters.telegram.handlers import admin_manage as h
from app.adapters.telegram.keyboards.admin_panel import panel_kb
from app.adapters.telegram.texts import admin_panel as p
from app.config import Settings
from app.core import admin_auth
from app.data import db, repo_admins


class FakeState:
    def __init__(self):
        self.name = None

    async def set_state(self, value):
        self.name = value

    async def clear(self):
        self.name = None


class FakeMsg:
    def __init__(self, uid=None, text=None):
        self.from_user = SimpleNamespace(id=uid)
        self.text = text
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append(text)


class FakeCb:
    def __init__(self, uid, data):
        self.from_user = SimpleNamespace(id=uid)
        self.data = data
        self.message = FakeMsg()
        self.alerts = []

    async def answer(self, text=None, show_alert=False):
        self.alerts.append(text)


def _session(conn, uid, active=True):
    end = (datetime.now() + timedelta(minutes=30)).strftime(admin_auth.FMT)
    repo_admins.save_auth_state(conn, uid, 0, None, end if active else None)


@pytest.fixture
def env(tmp_path):
    path = tmp_path / "t.db"
    (tmp_path / "b").mkdir()
    db.migrate(path, tmp_path / "b")
    conn = db.connect(path)
    repo_admins.ensure_owner(conn, 7)
    _session(conn, 7)
    conn.close()
    return Settings("tok", 7, path, tmp_path), FakeState()


def get(settings, uid):
    conn = db.connect(settings.db_path)
    try:
        return repo_admins.get_admin(conn, uid)
    finally:
        conn.close()


def add_editor_row(settings, uid=55, with_session=True):
    conn = db.connect(settings.db_path)
    repo_admins.add_admin(conn, uid, "editor")
    if with_session:
        _session(conn, uid)
    conn.close()


def test_owner_adds_editor_and_sees_temp_once(env):
    settings, state = env
    asyncio.run(h.on_add(FakeCb(7, "adm:add"), state, settings))
    assert state.name is h.AddAdmin.ask_id
    msg = FakeMsg(7, "55")
    asyncio.run(h.on_new_id(msg, state, settings))
    editor = get(settings, 55)
    assert editor.role == "editor" and editor.must_change == 1
    assert state.name is None and len(msg.answers) == 1
    words = msg.answers[0].split()
    assert any(w.isascii() and w.isalnum() and len(w) == 14 for w in words)


def test_stranger_and_editor_get_no_reply(env):
    settings, state = env
    add_editor_row(settings)
    for uid in (999, 55):
        cb = FakeCb(uid, "adm:add")
        asyncio.run(h.on_add(cb, state, settings))
        assert state.name is None and cb.message.answers == []


def test_owner_without_session_is_silent(env):
    settings, state = env
    conn = db.connect(settings.db_path)
    _session(conn, 7, active=False)
    conn.close()
    cb = FakeCb(7, "adm:add")
    asyncio.run(h.on_add(cb, state, settings))
    assert state.name is None and cb.message.answers == []


def test_bad_id_rejected(env):
    settings, state = env
    state.name = h.AddAdmin.ask_id
    msg = FakeMsg(7, "abc")
    asyncio.run(h.on_new_id(msg, state, settings))
    assert msg.answers == [p.BAD_ID] and state.name is not None


def test_remove_editor(env):
    settings, state = env
    add_editor_row(settings)
    cb = FakeCb(7, "adm:rm:55")
    asyncio.run(h.on_remove(cb, settings))
    assert get(settings, 55).is_active == 0
    assert cb.message.answers == [p.STATUS["ok"]]


def test_owner_cannot_be_removed(env):
    settings, state = env
    cb = FakeCb(7, "adm:rm:7")
    asyncio.run(h.on_remove(cb, settings))
    assert cb.message.answers == [p.STATUS["cannot_remove_owner"]]
    assert get(settings, 7).is_active == 1


def test_reset_password_shows_temp_and_forces_change(env):
    settings, state = env
    add_editor_row(settings)
    cb = FakeCb(7, "adm:rs:55")
    asyncio.run(h.on_reset(cb, settings))
    assert get(settings, 55).must_change == 1
    assert "رمز موقتی" in cb.message.answers[0]


def test_only_owner_sees_manage_button():
    assert panel_kb("editor") is None
    assert len(panel_kb("owner").inline_keyboard) == 1
