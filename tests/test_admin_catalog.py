"""تست کاتالوگ خودرو (منطق، فرم و دسترسی)."""
import asyncio
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from app.adapters.telegram.handlers import admin_catalog as h
from app.adapters.telegram.texts import catalog as c
from app.config import Settings
from app.core import admin_auth, catalog
from app.data import db, repo_admins, repo_catalog


class FakeState:
    def __init__(self):
        self.name = None
        self.data = {}

    async def set_state(self, value):
        self.name = value

    async def update_data(self, **kwargs):
        self.data.update(kwargs)

    async def get_data(self):
        return dict(self.data)

    async def clear(self):
        self.name = None
        self.data = {}


class FakeMsg:
    def __init__(self, uid=None, text=None):
        self.from_user = SimpleNamespace(id=uid)
        self.text = text
        self.answers = []
        self.edits = []

    async def answer(self, text, **kwargs):
        self.answers.append(text)

    async def edit_text(self, text, reply_markup=None):
        self.edits.append(text)


class FakeCb:
    def __init__(self, uid, data):
        self.from_user = SimpleNamespace(id=uid)
        self.data = data
        self.message = FakeMsg()

    async def answer(self, text=None, show_alert=False):
        pass


def _live(minutes=30):
    return (datetime.now() + timedelta(minutes=minutes)).strftime(admin_auth.FMT)


@pytest.fixture
def settings(tmp_path):
    path = tmp_path / "t.db"
    (tmp_path / "b").mkdir()
    db.migrate(path, tmp_path / "b")
    conn = db.connect(path)
    repo_admins.ensure_owner(conn, 7)
    repo_admins.save_auth_state(conn, 7, 0, None, _live())
    repo_admins.add_admin(conn, 55, "editor")
    repo_admins.save_auth_state(conn, 55, 0, None, _live())
    conn.close()
    return Settings("tok", 7, path, tmp_path)


def _seed(settings):
    conn = db.connect(settings.db_path)
    bid = repo_catalog.add_brand(conn, "پژو")
    mid = repo_catalog.add_model(conn, bid, "۲۰۶")
    repo_catalog.add_trim(conn, mid, "تیپ ۲")
    conn.close()
    return bid, mid


def test_core_add_chain_and_duplicate(conn):
    assert catalog.add_item(conn, "brand", 0, "  پژو  ") == "ok"
    brand = repo_catalog.list_brands(conn)[0]
    assert brand["name"] == "پژو"
    assert catalog.add_item(conn, "brand", 0, "پژو") == "exists"
    assert catalog.add_item(conn, "model", brand["id"], "۲۰۶") == "ok"
    mid = repo_catalog.list_models(conn, brand["id"])[0]["id"]
    assert catalog.add_item(conn, "trim", mid, "تیپ ۲") == "ok"
    assert [t["name"] for t in repo_catalog.list_trims(conn, mid)] == ["تیپ ۲"]


def test_core_rejects_bad_names_and_missing_parent(conn):
    for bad in ("", "   ", "x" * 41, "/start"):
        assert catalog.add_item(conn, "brand", 0, bad) == "bad_name"
    assert catalog.add_item(conn, "model", 999, "ab") == "no_parent"
    assert catalog.add_item(conn, "trim", 999, "ab") == "no_parent"
    assert repo_catalog.list_brands(conn) == []


def test_owner_adds_brand_via_form(settings):
    state = FakeState()
    asyncio.run(h.on_new(FakeCb(7, "cat:nb"), state, settings))
    assert state.name is h.AddItem.name
    assert state.data == {"kind": "brand", "parent": 0}
    msg = FakeMsg(7, "پژو")
    asyncio.run(h.on_name(msg, state, settings))
    assert msg.answers[0] == c.STATUS["ok"] and state.name is None
    conn = db.connect(settings.db_path)
    assert [b["name"] for b in repo_catalog.list_brands(conn)] == ["پژو"]
    conn.close()


def test_add_model_and_trim_through_form(settings):
    conn = db.connect(settings.db_path)
    bid = repo_catalog.add_brand(conn, "پژو")
    conn.close()
    state = FakeState()
    asyncio.run(h.on_new(FakeCb(7, f"cat:nm:{bid}"), state, settings))
    msg = FakeMsg(7, "۲۰۶")
    asyncio.run(h.on_name(msg, state, settings))
    assert msg.answers[0] == c.STATUS["ok"]
    assert len(msg.answers) == 2 and "پژو" in msg.answers[1]
    conn = db.connect(settings.db_path)
    mid = repo_catalog.list_models(conn, bid)[0]["id"]
    conn.close()
    asyncio.run(h.on_new(FakeCb(7, f"cat:nt:{mid}"), state, settings))
    msg2 = FakeMsg(7, "تیپ ۲")
    asyncio.run(h.on_name(msg2, state, settings))
    assert msg2.answers[0] == c.STATUS["ok"] and "تیپ ۲" in msg2.answers[1]


def test_duplicate_name_reported(settings):
    _seed(settings)
    state = FakeState()
    asyncio.run(h.on_new(FakeCb(7, "cat:nb"), state, settings))
    msg = FakeMsg(7, "پژو")
    asyncio.run(h.on_name(msg, state, settings))
    assert msg.answers[0] == c.STATUS["exists"]


def test_bad_name_keeps_waiting(settings):
    state = FakeState()
    asyncio.run(h.on_new(FakeCb(7, "cat:nb"), state, settings))
    msg = FakeMsg(7, "x" * 41)
    asyncio.run(h.on_name(msg, state, settings))
    assert msg.answers == [c.BAD_NAME] and state.name is not None


def test_views_show_names(settings):
    bid, mid = _seed(settings)
    cb = FakeCb(7, f"cat:b:{bid}")
    asyncio.run(h.on_brand(cb, settings))
    assert "پژو" in cb.message.edits[0]
    cb2 = FakeCb(7, f"cat:m:{mid}")
    asyncio.run(h.on_model(cb2, settings))
    assert "تیپ ۲" in cb2.message.edits[0]


def test_editor_allowed_stranger_silent(settings):
    ok = FakeCb(55, "adm:cat")
    asyncio.run(h.on_catalog(ok, settings))
    assert ok.message.edits == [c.BRANDS_TITLE]
    stranger = FakeCb(999, "adm:cat")
    asyncio.run(h.on_catalog(stranger, settings))
    assert stranger.message.edits == []


def test_expired_session_is_silent(settings):
    conn = db.connect(settings.db_path)
    repo_admins.save_auth_state(conn, 7, 0, None, _live(-1))
    conn.close()
    state = FakeState()
    cb = FakeCb(7, "cat:nb")
    asyncio.run(h.on_new(cb, state, settings))
    assert state.name is None and cb.message.answers == []


def test_cancel_clears_state(settings):
    state = FakeState()
    asyncio.run(h.on_new(FakeCb(7, "cat:nb"), state, settings))
    cb = FakeCb(7, "cat:x")
    asyncio.run(h.on_cancel(cb, state))
    assert state.name is None and cb.message.answers == [c.CANCELLED]
