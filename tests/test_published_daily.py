"""Tests for the user-facing published daily table (step 4-3)."""
import asyncio
import sqlite3
from pathlib import Path
from types import SimpleNamespace

from app.adapters.telegram.handlers import car_price
from app.adapters.telegram.texts import car_price as ct
from app.adapters.telegram.texts import daily_prices as dp
from app.adapters.telegram.texts import menu
from app.core import published_view
from app.data import repo_published

MIGRATION = Path("app/data/migrations/004_published_daily.sql")
SOURCE = Path("app/data/migrations/006_published_source.sql")
ROW = {"name": "تست", "year": 1404, "price_m": 1000, "change_m": 0}


class _State:
    cleared = False

    async def clear(self):
        self.cleared = True


def make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(MIGRATION.read_text(encoding="utf-8"))
    conn.executescript(SOURCE.read_text(encoding="utf-8"))
    return conn


def test_get_empty():
    assert repo_published.get(make_conn()) is None


def test_replace_keeps_single_row():
    conn = make_conn()
    repo_published.replace(conn, "2026-10-25", [ROW])
    repo_published.replace(conn, "2026-10-26", [ROW, ROW])
    data = repo_published.get(conn)
    assert data["day"] == "2026-10-26" and len(data["rows"]) == 2
    assert conn.execute("SELECT COUNT(*) FROM published_daily").fetchone()[0] == 1


def test_parts_converts_to_tehran():
    data = {"published_at": "2026-10-25 01:19:15"}
    day_text, local = published_view.parts(data, dp)
    assert (local.hour, local.minute) == (4, 49)
    assert "۱۴۰۵" in day_text


def test_parts_crosses_midnight():
    data = {"published_at": "2026-10-25 21:00:00"}
    _, local = published_view.parts(data, dp)
    assert local.day == 26 and local.hour == 0


def _message(sent: list):
    async def answer(text, **kwargs):
        sent.append(text)
    return SimpleNamespace(
        text=menu.BTN_CAR_PRICE, chat=SimpleNamespace(id=1), answer=answer)


def test_handler_nothing_published(monkeypatch):
    sent = []
    monkeypatch.setattr(car_price.dbrun, "run", lambda *a: None)
    asyncio.run(car_price.on_car_price(_message(sent), None, None, _State()))
    assert sent == [ct.SOON]


def test_handler_sends_table(monkeypatch):
    calls = []
    data = {"day": "2026-10-25", "rows": [ROW],
            "published_at": "2026-10-25 01:19:15"}
    monkeypatch.setattr(car_price.dbrun, "run", lambda *a: data)

    async def fake_send(bot, chat_id, rows, day_text, markup, now):
        calls.append((chat_id, rows, markup, now.hour))
        return "rich"

    monkeypatch.setattr(car_price.daily_send, "send_table", fake_send)
    asyncio.run(car_price.on_car_price(_message([]), None, None, _State()))
    assert calls == [(1, [ROW], None, 4)]
