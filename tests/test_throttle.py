"""Tests for the per-user throttle middleware."""
import asyncio
from types import SimpleNamespace

from app.adapters.telegram.throttle import DROP, NOTIFY, OK, ThrottleMiddleware


class Clock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


class FakeEvent:
    def __init__(self, uid):
        self.from_user = SimpleNamespace(id=uid)
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append(text)


def _mw(clock, **kw):
    args = dict(max_events=3, window=10.0, block=10.0, clock=clock)
    args.update(kw)
    return ThrottleMiddleware(**args)


def test_blocks_after_limit_then_recovers():
    clock = Clock()
    mw = _mw(clock)
    assert [mw.check(1) for _ in range(3)] == [OK, OK, OK]
    assert mw.check(1) == NOTIFY
    assert mw.check(1) == DROP
    clock.t += 11
    assert mw.check(1) == OK


def test_users_are_independent():
    clock = Clock()
    mw = _mw(clock)
    for _ in range(4):
        mw.check(1)
    assert mw.check(2) == OK


def test_exempt_user_never_blocked():
    mw = _mw(Clock(), exempt_ids=(7,))
    assert all(mw.check(7) == OK for _ in range(100))


def test_slow_user_never_blocked():
    clock = Clock()
    mw = _mw(clock)
    for _ in range(20):
        assert mw.check(1) == OK
        clock.t += 5


def test_middleware_calls_handler_and_notifies_once():
    clock = Clock()
    mw = _mw(clock)
    calls = []

    async def handler(event, data):
        calls.append(1)
        return "handled"

    events = [FakeEvent(1) for _ in range(6)]

    async def run():
        for ev in events:
            await mw(handler, ev, {})

    asyncio.run(run())
    assert len(calls) == 3
    assert sum(len(ev.answers) for ev in events) == 1


def test_event_without_user_passes_through():
    mw = _mw(Clock())

    async def handler(event, data):
        return "handled"

    ev = SimpleNamespace()
    assert asyncio.run(mw(handler, ev, {})) == "handled"
