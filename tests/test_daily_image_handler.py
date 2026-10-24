"""Tests for the image button handler (no real Telegram)."""
import asyncio
from unittest.mock import AsyncMock, MagicMock

from app.adapters.telegram.handlers import daily_image

ROWS = [{"name": "Rana", "year": 1405, "price_m": 2375, "change_m": 80}]


def _cb():
    cb = MagicMock()
    cb.from_user.id = 1
    cb.answer = AsyncMock()
    cb.message.answer = AsyncMock()
    cb.message.answer_photo = AsyncMock()
    return cb


def _state(rows):
    state = MagicMock()
    state.get_data = AsyncMock(return_value={"rows": rows})
    state.clear = AsyncMock()
    return state


def test_empty_rows_shows_alert(monkeypatch):
    monkeypatch.setattr(daily_image, "active_admin", lambda s, i: object())
    cb = _cb()
    asyncio.run(daily_image.on_pic(cb, _state([]), MagicMock()))
    cb.answer.assert_awaited_once()
    cb.message.answer_photo.assert_not_awaited()


def test_rows_send_photo(monkeypatch):
    monkeypatch.setattr(daily_image, "active_admin", lambda s, i: object())
    cb = _cb()
    asyncio.run(daily_image.on_pic(cb, _state(ROWS), MagicMock()))
    cb.message.answer_photo.assert_awaited_once()


def test_non_admin_gets_nothing(monkeypatch):
    monkeypatch.setattr(daily_image, "active_admin", lambda s, i: None)
    cb = _cb()
    asyncio.run(daily_image.on_pic(cb, _state(ROWS), MagicMock()))
    cb.message.answer_photo.assert_not_awaited()
