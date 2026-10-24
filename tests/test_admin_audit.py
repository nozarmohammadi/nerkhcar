"""تست نمایش لاگ ممیزی."""
import asyncio
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from app.adapters.telegram.handlers import admin_audit as h
from app.adapters.telegram.texts import admin_panel as p
from app.config import Settings
from app.core import admin_auth, audit_view
from app.data import db, repo_admins, repo_audit


class FakeMsg:
    def __init__(self):
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append(text)


class FakeCb:
    def __init__(self, uid):
        self.from_user = SimpleNamespace(id=uid)
        self.message = FakeMsg()

    async def answer(self, text=None, show_alert=False):
        pass


def _session(conn, uid, active=True):
    end = (datetime.now() + timedelta(minutes=30)).strftime(admin_auth.FMT)
    repo_admins.save_auth_state(conn, uid, 0, None, end if active else None)


@pytest.fixture
def settings(tmp_path):
    path = tmp_path / "t.db"
    (tmp_path / "b").mkdir()
    db.migrate(path, tmp_path / "b")
    conn = db.connect(path)
    repo_admins.ensure_owner(conn, 7)
    _session(conn, 7)
    repo_admins.add_admin(conn, 55, "editor")
    _session(conn, 55)
    conn.close()
    return Settings("tok", 7, path, tmp_path)


def _add(settings, admin_id, action, detail=""):
    conn = db.connect(settings.db_path)
    repo_audit.add_entry(conn, admin_id, action, detail)
    conn.close()


def _view(settings, uid):
    cb = FakeCb(uid)
    asyncio.run(h.on_log(cb, settings))
    return cb.message.answers


def test_owner_sees_newest_first(settings):
    _add(settings, 55, "login_fail")
    _add(settings, 7, "admin_added", "id=9 role=editor")
    text = _view(settings, 7)[0]
    first = text.index(p.ACTION_LABELS["admin_added"])
    second = text.index(p.ACTION_LABELS["login_fail"])
    assert first < second and "id=9" in text


def test_empty_log_message(settings):
    assert _view(settings, 7) == [p.LOG_EMPTY]


def test_editor_and_stranger_get_no_reply(settings):
    _add(settings, 7, "login_ok")
    assert _view(settings, 55) == []
    assert _view(settings, 999) == []


def test_owner_without_session_is_silent(settings):
    conn = db.connect(settings.db_path)
    _session(conn, 7, active=False)
    conn.close()
    assert _view(settings, 7) == []


def test_only_ten_rows(conn):
    for i in range(15):
        repo_audit.add_entry(conn, 1, "login_ok", f"n={i}")
    assert len(audit_view.recent_rows(conn)) == 10


def test_detail_cut_and_none_admin(conn):
    repo_audit.add_entry(conn, None, "owner_created", "x" * 100)
    row = audit_view.recent_rows(conn)[0]
    assert len(row["detail"]) == 40 and row["who"] == "-"
