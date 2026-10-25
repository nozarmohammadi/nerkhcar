"""Daily car prices: build and send the vertical price video (button dp:vid)."""
import asyncio
import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery

from app.adapters import video_ffmpeg
from app.adapters.telegram.guard import active_admin
from app.adapters.telegram.texts import daily_prices as t
from app.config import Settings
from app.core import daily_text, daily_video

log = logging.getLogger("nerkhcar")
router = Router()
router.callback_query.filter(F.message.chat.type == "private")
_LOCK = asyncio.Lock()


def _build(rows: list[dict]) -> bytes:
    """Blocking work: render the frames and run ffmpeg (run in a thread)."""
    frames = daily_video.render_frames(rows, daily_text.date_text(t), t)
    return video_ffmpeg.make_video(frames)


async def _send(cb: CallbackQuery, rows: list[dict]) -> None:
    note = await cb.message.answer(t.VID_WAIT)
    try:
        video = await asyncio.to_thread(_build, rows)
    except Exception:
        log.exception("daily price video failed")
        await note.edit_text(t.VID_FAIL)
        return
    await cb.message.answer_video(
        BufferedInputFile(video, "prices.mp4"),
        width=720, height=1280, supports_streaming=True)
    try:
        await note.delete()
    except TelegramBadRequest:
        pass  # the status message is already gone


@router.callback_query(F.data == "dp:vid")
async def on_video(
    cb: CallbackQuery, state: FSMContext, settings: Settings
) -> None:
    if active_admin(settings, cb.from_user.id) is None:
        await state.clear()
        await cb.answer()
        return
    rows = (await state.get_data()).get("rows")
    if not rows:
        await cb.answer(t.VID_EMPTY, show_alert=True)
        return
    if _LOCK.locked():
        await cb.answer(t.VID_BUSY, show_alert=True)
        return
    async with _LOCK:
        await cb.answer()
        await _send(cb, rows)
