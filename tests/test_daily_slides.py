"""Tests for one image slide per source photo."""
import asyncio
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock

from PIL import Image

from app.adapters.telegram.handlers import daily_image as handler
from app.adapters.telegram.texts import daily_prices as t
from app.core import daily_image, daily_text


def _row(name, photo=None):
    row = {"name": name, "year": 1405, "price_m": 1000, "change_m": 5,
           "flags": []}
    if photo is not None:
        row["photo"] = photo
    return row


def _cb():
    cb = MagicMock()
    cb.from_user.id = 1
    cb.answer = AsyncMock()
    cb.message.answer = AsyncMock()
    cb.message.answer_photo = AsyncMock()
    cb.message.answer_media_group = AsyncMock()
    return cb


def _press(monkeypatch, rows):
    monkeypatch.setattr(handler, "active_admin", lambda s, i: object())
    state = MagicMock()
    state.get_data = AsyncMock(return_value={"rows": rows})
    cb = _cb()
    asyncio.run(handler.on_pic(cb, state, MagicMock()))
    return cb


def test_merge_rows_tags_photo():
    merged = daily_text.merge_rows([], [_row("A")], 3)
    assert merged[0]["photo"] == 3


def test_merge_rows_without_photo_adds_no_tag():
    assert "photo" not in daily_text.merge_rows([], [_row("A")])[0]


def test_group_rows_per_photo():
    rows = [_row("A", 1), _row("B", 2), _row("C", 1)]
    names = [[r["name"] for r in g] for g in daily_text.group_rows(rows)]
    assert names == [["A", "C"], ["B"]]


def test_group_rows_legacy_rows_are_one_group():
    assert len(daily_text.group_rows([_row("A"), _row("B")])) == 1


def test_render_all_one_png_per_photo():
    rows = [_row("A", 1), _row("B", 2), _row("C", 3)]
    images = daily_image.render_all(rows, "d", t)
    assert len(images) == 3
    assert Image.open(BytesIO(images[0])).size[0] == daily_image.WIDTH


def test_handler_sends_album_for_many_slides(monkeypatch):
    cb = _press(monkeypatch, [_row("A", 1), _row("B", 2)])
    cb.message.answer_media_group.assert_awaited_once()
    cb.message.answer_photo.assert_not_awaited()


def test_handler_splits_albums_over_ten(monkeypatch):
    rows = [_row(f"N{i}", i) for i in range(1, 12)]
    cb = _press(monkeypatch, rows)
    cb.message.answer_media_group.assert_awaited_once()
    cb.message.answer_photo.assert_awaited_once()
