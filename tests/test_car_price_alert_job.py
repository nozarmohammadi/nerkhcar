import asyncio
from datetime import datetime
from types import SimpleNamespace

from app.adapters.telegram.texts import car_price as t
from app.jobs import car_price_job as job

SETTINGS = SimpleNamespace(owner_id=7)
SAT_19 = datetime(2026, 10, 24, 19, 0)
DAY = "1405-08-02"


class Bot:
    def __init__(self, fail=False):
        self.sent = []
        self.fail = fail

    async def send_message(self, chat_id, text):
        if self.fail:
            raise RuntimeError("boom")
        self.sent.append((chat_id, text))


def test_late_alert_sent_once(monkeypatch):
    monkeypatch.setattr(job, "already_saved", lambda d: False)
    bot, state = Bot(), {"fails": 0, "sent": set()}
    for _ in range(2):
        asyncio.run(job._alert(SETTINGS, bot, SAT_19, DAY, state))
    assert bot.sent == [(7, t.ALERT_LATE)]


def test_fail_alert(monkeypatch):
    monkeypatch.setattr(job, "already_saved", lambda d: True)
    bot, state = Bot(), {"fails": 3, "sent": set()}
    asyncio.run(job._alert(SETTINGS, bot, SAT_19, DAY, state))
    assert bot.sent == [(7, t.ALERT_FAIL)]


def test_send_error_does_not_raise(monkeypatch):
    monkeypatch.setattr(job, "already_saved", lambda d: False)
    state = {"fails": 0, "sent": set()}
    asyncio.run(job._alert(SETTINGS, Bot(fail=True), SAT_19, DAY, state))
    assert state["sent"] == set()


def test_no_bot_is_safe(monkeypatch):
    monkeypatch.setattr(job, "already_saved", lambda d: False)
    state = {"fails": 0, "sent": set()}
    asyncio.run(job._alert(SETTINGS, None, SAT_19, DAY, state))
    assert state["sent"] == set()
