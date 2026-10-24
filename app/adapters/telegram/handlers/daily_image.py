"""Daily car prices: send one PNG slide per source photo (button dp:pic)."""
import asyncio
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, InputMediaPhoto

from app.adapters.telegram.guard import active_admin
from app.adapters.telegram.texts import daily_prices as t
from app.config import Settings
from app.core import daily_image, daily_text

log = logging.getLogger("nerkhcar")
router = Router()
router.callback_query.filter(F.message.chat.type == "private")
ALBUM_MAX = 10


async def _send_slides(message, images: list[bytes]) -> None:
    """Send a single photo, or albums of up to ALBUM_MAX slides."""
    for start in range(0, len(images), ALBUM_MAX):
        part = images[start:start + ALBUM_MAX]
        files = [
            BufferedInputFile(png, f"slide{start + i + 1}.png")
            for i, png in enumerate(part)
        ]
        if len(files) == 1:
            await message.answer_photo(files[0])
        else:
            await message.answer_media_group(
                [InputMediaPhoto(media=f) for f in files])


@router.callback_query(F.data == "dp:pic")
async def on_pic(
    cb: CallbackQuery, state: FSMContext, settings: Settings
) -> None:
    if active_admin(settings, cb.from_user.id) is None:
        await state.clear()
        await cb.answer()
        return
    rows = (await state.get_data()).get("rows")
    if not rows:
        await cb.answer(t.IMG_EMPTY, show_alert=True)
        return
    await cb.answer()
    try:
        images = await asyncio.to_thread(
            daily_image.render_all, rows, daily_text.date_text(t), t)
    except Exception:
        log.exception("daily price image failed")
        await cb.message.answer(t.IMG_FAIL)
        return
    await _send_slides(cb.message, images)
