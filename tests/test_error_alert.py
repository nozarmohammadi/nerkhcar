"""Tests for the owner alert on unexpected errors."""
import asyncio
from types import SimpleNamespace

from app import main as main_mod
from app.core.error_alert import ErrorAlertGate


class Clock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


class FakeBot:
    def __init__(self, fail=False):
        self.sent = []
        self.fail = fail

    async def send_message(self, chat_id, text):
        if self.fail:
            raise RuntimeError("boom")
        self.sent.append((chat_id, text))


class FakeMsg:
    def __init__(self):
        self.answers = []

    async def answer(self, text):
        self.answers.append(text)


def _event():
    msg = FakeMsg()
    exc = ValueError("secret detail")
    return SimpleNamespace(exception=exc, update=SimpleNamespace(message=msg)), msg


def _gate(monkeypatch, clock):
    monkeypatch.setattr(main_mod, "_ALERT_GATE", ErrorAlertGate(600, clock))


def test_gate_cooldown():
    clock = Clock()
    gate = ErrorAlertGate(600, clock)
    assert gate.allow() is True
    assert gate.allow() is False
    clock.t += 601
    assert gate.allow() is True


def test_owner_gets_one_alert_without_details(monkeypatch):
    _gate(monkeypatch, Clock())
    bot = FakeBot()
    settings = SimpleNamespace(owner_id=42)
    ev1, msg1 = _event()
    ev2, _ = _event()
    assert asyncio.run(main_mod.on_error(ev1, bot=bot, settings=settings)) is True
    assert asyncio.run(main_mod.on_error(ev2, bot=bot, settings=settings)) is True
    assert len(bot.sent) == 1
    assert bot.sent[0][0] == 42
    assert "ValueError" in bot.sent[0][1]
    assert "secret detail" not in bot.sent[0][1]
    assert len(msg1.answers) == 1


def test_works_without_bot(monkeypatch):
    _gate(monkeypatch, Clock())
    ev, msg = _event()
    assert asyncio.run(main_mod.on_error(ev)) is True
    assert len(msg.answers) == 1


def test_send_failure_never_breaks(monkeypatch):
    _gate(monkeypatch, Clock())
    ev, msg = _event()
    ok = asyncio.run(
        main_mod.on_error(ev, bot=FakeBot(fail=True), settings=SimpleNamespace(owner_id=1))
    )
    assert ok is True
    assert len(msg.answers) == 1
