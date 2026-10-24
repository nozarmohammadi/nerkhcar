"""تست قیمت روز خودرو (پیام‌های ساختگی؛ بدون شبکه)."""
import asyncio
import io
import json
from datetime import date
from types import SimpleNamespace

from aiogram.exceptions import TelegramAPIError

from app import main
from app.adapters.telegram import daily_send
from app.adapters.telegram.handlers import daily_prices as h
from app.adapters.telegram.keyboards import admin_panel as k_panel
from app.adapters.telegram.texts import daily_prices as t
from app.core import daily_text, jalali, table_parse

RAW = [
    {"name": "سهند", "year": 1405, "price": 1810000000, "change": 5000000},
    {"name": "ساینا اس", "year": 1405, "price": 1720000000, "change": -15000000},
    {"name": "ساینا اتومات", "year": 1405, "price": None, "change": None},
]
AI_REPLY = json.dumps(RAW, ensure_ascii=False)


class Boom(TelegramAPIError):
    def __init__(self):
        Exception.__init__(self, "boom")
        self.message = "boom"


class FakeBot:
    def __init__(self, fail=False):
        self.fail = fail
        self.rich, self.sent, self.edits = [], [], []

    async def send_rich_message(self, **kwargs):
        if self.fail:
            raise Boom()
        self.rich.append(kwargs)

    async def send_message(self, **kwargs):
        self.sent.append(kwargs["text"])

    async def edit_message_text(self, **kwargs):
        self.edits.append(kwargs)

    async def download(self, file):
        return io.BytesIO(b"img")


class FakeState:
    def __init__(self):
        self.data = {}

    async def get_data(self):
        return dict(self.data)

    async def update_data(self, **kwargs):
        self.data.update(kwargs)

    async def clear(self):
        self.data = {}


class FakeMsg:
    def __init__(self, sent, photo=None):
        self.from_user = SimpleNamespace(id=7)
        self.chat = SimpleNamespace(id=1)
        self.photo = photo
        self.document = None
        self.sent = sent
        self.edited = []

    async def answer(self, text, **kwargs):
        self.sent.append(text)
        return SimpleNamespace(message_id=5)

    async def edit_text(self, text, **kwargs):
        self.edited.append(text)


class FakeCb:
    def __init__(self, sent):
        self.from_user = SimpleNamespace(id=7)
        self.message = FakeMsg(sent)

    async def answer(self, text=None, show_alert=False):
        return None


def _setup(monkeypatch):
    async def fake_ai(image, mime, model):
        return "ok", AI_REPLY

    monkeypatch.setattr(h, "active_admin", lambda s, uid: object())
    monkeypatch.setattr(h.gemini, "make_extractor", lambda key: fake_ai)
    import tempfile
    from pathlib import Path
    from app.data import db
    folder = Path(tempfile.mkdtemp())
    (folder / "b").mkdir()
    db.migrate(folder / "t.db", folder / "b")
    return SimpleNamespace(
        gemini_key="k", vision_models=("m",), db_path=folder / "t.db")


def _ready_rows():
    return daily_text.merge_rows([], table_parse.normalize_rows(RAW))


def test_merge_drops_blocked_and_replaces_duplicates():
    total = _ready_rows()
    assert [r["name"] for r in total] == ["سهند", "ساینا اس"]
    newer = table_parse.normalize_rows([dict(RAW[0], price=1900000000)])
    total = daily_text.merge_rows(total, newer)
    assert len(total) == 2 and total[0]["price_m"] == 1900


def test_build_text_has_prices_and_arrows():
    text = daily_text.build_text(_ready_rows(), "2026-10-24", t)
    assert "۱٬۸۱۰" in text and "📈" in text and "📉" in text
    assert "ساینا اتومات" not in text and "2026-10-24" in text


def test_html_table_escapes_and_has_header():
    rows = [{"name": "a<b", "year": 1405, "price_m": 1810,
             "change_m": 5.0, "flags": []}]
    html = daily_text.build_html(rows, "2026-10-24", t)
    assert "<table" in html and "a&lt;b" in html and "۱٬۸۱۰" in html
    assert t.TBL_HEAD[0] in html and "📈" in html


def test_text_chunks_limit():
    text = "\n".join("x" * 100 for _ in range(100))
    chunks = daily_text.text_chunks(text)
    assert len(chunks) > 1
    assert all(len(c) <= daily_text.CHUNK_CHARS for c in chunks)


def test_send_table_rich_and_fallback():
    ok, bad = FakeBot(), FakeBot(fail=True)
    rows = _ready_rows()
    assert asyncio.run(daily_send.send_table(ok, 1, rows, "d", None)) == "rich"
    assert len(ok.rich) == 1 and not ok.sent
    assert asyncio.run(daily_send.send_table(bad, 1, rows, "d", None)) == "text"
    assert bad.sent and not bad.rich


def test_one_status_message_edited_per_photo(monkeypatch):
    settings = _setup(monkeypatch)
    state, bot, sent = FakeState(), FakeBot(), []
    state.data = {"rows": [], "photos": 0}

    async def run():
        for _ in range(2):
            msg = FakeMsg(sent, photo=[SimpleNamespace(file_size=10)])
            await h.on_photo(msg, state, settings, bot)

    asyncio.run(run())
    assert len(sent) == 1 and len(bot.edits) == 3
    assert len(state.data["rows"]) == 2 and state.data["photos"] == 2


def test_done_sends_one_table(monkeypatch):
    _setup(monkeypatch)
    state, bot, sent = FakeState(), FakeBot(), []
    state.data = {"rows": _ready_rows()}
    cb = FakeCb(sent)
    asyncio.run(h.on_done(cb, state, SimpleNamespace(), bot))
    assert len(bot.rich) == 1
    assert "<table" in bot.rich[0]["rich_message"].html
    assert cb.message.edited == [t.FINISHED.format(rows=2)]


def test_panel_has_daily_button():
    for role in ("owner", "editor"):
        kb = k_panel.panel_kb(role)
        assert "dp:go" in [row[0].callback_data for row in kb.inline_keyboard]


def test_router_registered():
    assert h.router in [m.router for m in main.ROUTER_MODULES]


def test_jalali_date_text():
    assert jalali.to_jalali(2026, 10, 24) == (1405, 8, 2)
    assert daily_text.date_text(t, date(2026, 10, 24)) == "۲ آبان ۱۴۰۵"


def test_compact_table_shape():
    html = daily_text.build_html(_ready_rows(), "d", t)
    table = html.split("<table")[1].split("</table>")[0]
    assert "1405" not in table and "میلیون" not in table
    assert "📈" in table and "📉" in table and "+" not in table
    assert "میلیون" in html.split("<table")[0]
