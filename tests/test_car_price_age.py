import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.adapters.telegram.handlers import car_price
from app.adapters.telegram.texts import car_price as t


class Msg:
    def __init__(self):
        self.sent = []
        self.chat = SimpleNamespace(id=1)

    async def answer(self, text, **kw):
        self.sent.append(text)


class State:
    async def clear(self):
        pass


def run(monkeypatch, hours):
    when = datetime.now(timezone.utc) - timedelta(hours=hours)
    data = {"day": "x", "rows": [{"name": "a"}],
            "published_at": when.strftime("%Y-%m-%d %H:%M:%S")}
    monkeypatch.setattr(car_price.dbrun, "run", lambda *a: data)
    calls = []

    async def fake_send(*a):
        calls.append(a)

    monkeypatch.setattr(car_price.daily_send, "send_table", fake_send)
    msg = Msg()
    asyncio.run(car_price.on_car_price(msg, None, None, State()))
    return msg.sent, calls


def test_fresh_sends_table_only(monkeypatch):
    sent, calls = run(monkeypatch, 2)
    assert sent == [] and len(calls) == 1


def test_old_warns_then_table(monkeypatch):
    sent, calls = run(monkeypatch, 40)
    assert sent == [t.OLD_NOTE] and len(calls) == 1


def test_expired_no_table(monkeypatch):
    sent, calls = run(monkeypatch, 80)
    assert sent == [t.EXPIRED] and calls == []
