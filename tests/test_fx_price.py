"""Tests for the FX, gold and coin button (phase 5)."""
import asyncio
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from aiogram.exceptions import TelegramAPIError

from app.adapters.telegram import fx_refresh, fx_send
from app.adapters.telegram.handlers import fx_price
from app.adapters.telegram.texts import fx as t
from app.core import fx_parse, fx_view
from app.data import repo_fx

FMT = "%Y-%m-%d %H:%M:%S"
HTML = (
    '<tr data-market-nameslug="price_dollar_rl" '
    'data-market-row="price_dollar_rl" data-title="" class="pointer" '
    'data-price="2,685,000"> <th><span class="flag"></span>دلار</th></tr>'
    '<tr data-market-row="other_key" data-price="5,000"> <th>نامربوط</th></tr>'
)


def _rows(minutes_old: int = 0) -> list[dict]:
    when = datetime.now(timezone.utc) - timedelta(minutes=minutes_old)
    return [
        {"symbol": s, "toman": 1000 + i, "fetched_at": when.strftime(FMT)}
        for i, s in enumerate(fx_parse.WANTED)
    ]


def test_parse_converts_rial_to_toman_and_filters():
    rows = fx_parse.parse_page(HTML)
    assert list(rows) == ["price_dollar_rl"]
    assert rows["price_dollar_rl"]["toman"] == 268500
    assert rows["price_dollar_rl"]["title"] == "دلار"


def test_parse_pages_first_page_wins():
    second = HTML.replace("2,685,000", "9,999,000")
    rows = fx_parse.parse_pages([HTML, second])
    assert rows["price_dollar_rl"]["toman"] == 268500


def test_stale_rules():
    now = datetime.now(timezone.utc)
    assert fx_view.is_stale([], 9, now)
    assert fx_view.is_stale(_rows()[:5], 9, now)
    assert not fx_view.is_stale(_rows(1), 9, now)
    assert fx_view.is_stale(_rows(10), 9, now)


def test_html_and_text_have_all_labels():
    html = fx_view.build_html(_rows(), "line", t)
    text = fx_view.build_text(_rows(), "line", t)
    assert "<table" in html
    for label in t.LABELS.values():
        assert label in html and label in text


def test_repo_roundtrip():
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        Path("app/data/migrations/001_init.sql").read_text(encoding="utf-8"))
    repo_fx.save_rows(conn, {"geram18": 100, "nim": 200})
    repo_fx.save_rows(conn, {"geram18": 150})
    rows = repo_fx.load_rows(conn, ("nim", "geram18", "rob"))
    assert [(r["symbol"], r["toman"]) for r in rows] == [("nim", 200), ("geram18", 150)]


def _patch_refresh(monkeypatch, rows):
    calls = []
    monkeypatch.setattr(fx_refresh, "_load", lambda s: rows)

    async def fake(settings):
        calls.append(1)

    monkeypatch.setattr(fx_refresh, "_refresh", fake)
    return calls


def test_fresh_rows_skip_refresh(monkeypatch):
    calls = _patch_refresh(monkeypatch, _rows(1))
    got = asyncio.run(fx_refresh.get_rows(None))
    assert len(got) == 9 and calls == []


def test_stale_rows_trigger_refresh(monkeypatch):
    calls = _patch_refresh(monkeypatch, _rows(30))
    asyncio.run(fx_refresh.get_rows(None))
    assert calls == [1]


class _Bot:
    def __init__(self, fail: bool):
        self.fail, self.rich, self.text = fail, [], []

    async def send_rich_message(self, **kw):
        if self.fail:
            raise TelegramAPIError(method=SimpleNamespace(), message="x")
        self.rich.append(kw)

    async def send_message(self, **kw):
        self.text.append(kw)


def test_send_table_rich_and_fallback():
    ok, bad = _Bot(False), _Bot(True)
    assert asyncio.run(fx_send.send_table(ok, 1, _rows())) == "rich"
    assert asyncio.run(fx_send.send_table(bad, 1, _rows())) == "text"
    assert len(ok.rich) == 1 and len(bad.text) == 1


class _State:
    cleared = False

    async def clear(self):
        self.cleared = True


def _message(sent: list):
    async def answer(text, **kw):
        sent.append(text)
    return SimpleNamespace(chat=SimpleNamespace(id=1), answer=answer)


def test_handler_nothing_available(monkeypatch):
    async def none(settings):
        return []

    monkeypatch.setattr(fx_price.fx_refresh, "get_rows", none)
    sent, state = [], _State()
    asyncio.run(fx_price.on_fx(_message(sent), None, None, state))
    assert sent == [t.SOON] and state.cleared


def test_handler_sends_table(monkeypatch):
    calls = []

    async def rows(settings):
        return _rows()

    async def send(bot, chat_id, data):
        calls.append((chat_id, len(data)))

    monkeypatch.setattr(fx_price.fx_refresh, "get_rows", rows)
    monkeypatch.setattr(fx_price.fx_send, "send_table", send)
    asyncio.run(fx_price.on_fx(_message([]), None, None, _State()))
    assert calls == [(1, 9)]
