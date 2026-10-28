"""Tests for the panel deny helper (expired session message)."""
import asyncio
from types import SimpleNamespace

from app.adapters.telegram import guard


def _cb(calls):
    async def answer(text=None, show_alert=False):
        calls.append((text, show_alert))
    return SimpleNamespace(from_user=SimpleNamespace(id=1), answer=answer)


def test_deny_explains_expired_session(monkeypatch):
    calls = []
    monkeypatch.setattr(guard, "active_admin", lambda settings, uid: None)
    asyncio.run(guard.deny(_cb(calls), None))
    assert calls == [(guard.SESSION_EXPIRED, True)]


def test_deny_is_silent_for_active_admin(monkeypatch):
    calls = []
    monkeypatch.setattr(guard, "active_admin", lambda settings, uid: object())
    asyncio.run(guard.deny(_cb(calls), None))
    assert calls == [(None, False)]
