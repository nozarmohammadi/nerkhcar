"""Daily car prices: send the table as a PNG image (button dp:pic)."""
import asyncio
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery

from app.adapters.telegram.guard import active_admin
from app.adapters.telegram.texts import daily_prices as t
from app.config import Settings
from app.core import daily_image, daily_text

log = logging.getLogger("nerkhcar")
router = Router()
router.callback_query.filter(F.message.chat.type == "private")


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
        png = await asyncio.to_thread(
            daily_image.render, rows, daily_text.date_text(t), t)
    except Exception:
        log.exception("daily price image failed")
        await cb.message.answer(t.IMG_FAIL)
        return
    await cb.message.answer_photo(BufferedInputFile(png, "prices.png"))
