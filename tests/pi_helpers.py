"""کمک‌های تست ثبت قیمت از عکس."""
from app.config import Settings
from types import SimpleNamespace
from app.core import admin_auth
from datetime import datetime
from app.data import db
from app.adapters.telegram.handlers import price_import as h
import io
import json
import pytest
from app.data import repo_admins
from app.data import repo_catalog
from datetime import timedelta


GOOD = json.dumps([
    {"name": "ساینا اس", "year": 1405, "price": 1720000000, "change": 15000000},
    {"name": "سهند", "year": 1405, "price": 1810000000, "change": 5000000},
    {"name": "ساینا اتومات", "year": 1405, "price": None, "change": None},
], ensure_ascii=False)


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


class FakeFile:
    def __init__(self, size=100):
        self.file_size = size


class FakeMsg:
    def __init__(self, uid=None, text=None, photo=None, document=None):
        self.from_user = SimpleNamespace(id=uid)
        self.text = text
        self.photo = photo
        self.document = document
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


class FakeBot:
    async def download(self, file):
        return io.BytesIO(b"img")


def _live(minutes=30):
    return (datetime.now() + timedelta(minutes=minutes)).strftime(admin_auth.FMT)


@pytest.fixture
def env(tmp_path):
    path = tmp_path / "t.db"
    (tmp_path / "b").mkdir()
    db.migrate(path, tmp_path / "b")
    conn = db.connect(path)
    repo_admins.ensure_owner(conn, 7)
    repo_admins.save_auth_state(conn, 7, 0, None, _live())
    brand = repo_catalog.add_brand(conn, "سایپا")
    conn.close()
    return Settings("tok", 7, path, tmp_path, gemini_key="k1"), brand


def _patch_ai(monkeypatch, status="ok", text=GOOD):
    async def fake(image, mime, model):
        return status, text

    monkeypatch.setattr(h.gemini, "make_extractor", lambda key: fake)


async def _to_review(settings, brand, state):
    await h.on_start(FakeCb(7, f"pi:{brand}"), state, settings)
    await h.on_source(FakeMsg(7, "auto_price"), state, settings)
    msg = FakeMsg(7, photo=[FakeFile()])
    await h.on_photo(msg, state, settings, FakeBot())
    return msg
