"""تست handler ورود ادمین با پیام‌های ساختگی (بدون تلگرام واقعی)."""
import asyncio
from types import SimpleNamespace

import pytest

from app.adapters.telegram.handlers import admin_login as h
from app.config import Settings
from app.core.passwords import hash_password
from app.data import db, repo_admins, repo_audit

PW = "Abcdef1234"


class FakeBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text):
        self.sent.append((chat_id, text))


class FakeState:
    def __init__(self):
        self.name = None

    async def set_state(self, value):
        self.name = value

    async def clear(self):
        self.name = None


class FakeMessage:
    def __init__(self, uid, text, bot):
        self.from_user = SimpleNamespace(id=uid)
        self.text = text
        self.bot = bot
        self.deleted = False
        self.answers = []

    async def delete(self):
        self.deleted = True

    async def answer(self, text, **kwargs):
        self.answers.append(text)


@pytest.fixture
def env(tmp_path):
    path = tmp_path / "t.db"
    (tmp_path / "b").mkdir()
    db.migrate(path, tmp_path / "b")
    return Settings("tok", 7, path, tmp_path), FakeBot(), FakeState()


def setup_owner(settings, with_password=True):
    conn = db.connect(settings.db_path)
    repo_admins.ensure_owner(conn, 7)
    if with_password:
        repo_admins.set_password(conn, 7, hash_password(PW))
    conn.close()


def admin_row(settings):
    conn = db.connect(settings.db_path)
    try:
        return repo_admins.get_admin(conn, 7)
    finally:
        conn.close()


def test_stranger_gets_no_reply(env):
    settings, bot, state = env
    setup_owner(settings)
    msg = FakeMessage(999, "/admin", bot)
    asyncio.run(h.on_admin(msg, state, settings))
    assert msg.answers == [] and state.name is None


def test_admin_is_asked_for_password(env):
    settings, bot, state = env
    setup_owner(settings)
    asyncio.run(h.on_admin(FakeMessage(7, "/admin", bot), state, settings))
    assert state.name is h.Login.password


def test_wrong_password_deleted_and_counted(env):
    settings, bot, state = env
    setup_owner(settings)
    msg = FakeMessage(7, "bad", bot)
    asyncio.run(h.on_password(msg, state, settings))
    assert msg.deleted
    assert admin_row(settings).failed_count == 1


def test_five_wrong_locks_and_alerts_owner(env):
    settings, bot, state = env
    setup_owner(settings)
    for _ in range(5):
        msg = FakeMessage(7, "bad", bot)
        asyncio.run(h.on_password(msg, state, settings))
        assert msg.deleted
    assert admin_row(settings).locked_until is not None
    assert bot.sent and bot.sent[0][0] == 7


def test_correct_password_opens_session(env):
    settings, bot, state = env
    setup_owner(settings)
    asyncio.run(h.on_password(FakeMessage(7, PW, bot), state, settings))
    assert admin_row(settings).session_until
    conn = db.connect(settings.db_path)
    entries = repo_audit.recent(conn)
    conn.close()
    assert entries[0]["action"] == "login_ok"
    assert all(PW not in str(e) for e in entries)


def test_owner_first_login_sets_password(env):
    settings, bot, state = env
    setup_owner(settings, with_password=False)
    asyncio.run(h.on_admin(FakeMessage(7, "/admin", bot), state, settings))
    assert state.name is h.Login.new_password
    weak = FakeMessage(7, "short", bot)
    asyncio.run(h.on_new_password(weak, state, settings))
    assert weak.deleted and admin_row(settings).pw_hash is None
    strong = FakeMessage(7, PW, bot)
    asyncio.run(h.on_new_password(strong, state, settings))
    assert strong.deleted and admin_row(settings).pw_hash.startswith("$argon2")
