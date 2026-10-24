"""قیمت روز خودرو: چند عکس ← یک پیام وضعیت ← جدول نهایی."""
import asyncio
import logging
from datetime import date

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.adapters.ai import gemini
from app.adapters.telegram import daily_send
from app.adapters.telegram.guard import active_admin
from app.adapters.telegram.keyboards import daily_prices as k
from app.adapters.telegram.texts import daily_prices as t
from app.config import Settings
from app.core import table_read
from app.core import daily_text

log = logging.getLogger("nerkhcar")
router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")
MAX_BYTES = 8 * 1024 * 1024
_LOCKS: dict[int, asyncio.Lock] = {}


class Daily(StatesGroup):
    photos = State()


def _lock(user_id: int) -> asyncio.Lock:
    return _LOCKS.setdefault(user_id, asyncio.Lock())


def _image_of(message: Message):
    if message.photo:
        return message.photo[-1], "image/jpeg"
    return message.document, message.document.mime_type


async def _show(bot: Bot, message: Message, state: FSMContext, text: str) -> None:
    """یک پیام وضعیت می‌سازد و بعد از آن همان را ویرایش می‌کند."""
    mid = (await state.get_data()).get("status_id")
    if mid is None:
        sent = await message.answer(text, reply_markup=k.collect_kb())
        await state.update_data(status_id=sent.message_id)
        return
    try:
        await bot.edit_message_text(
            text=text, chat_id=message.chat.id, message_id=mid,
            reply_markup=k.collect_kb())
    except TelegramBadRequest as exc:
        log.debug("ویرایش وضعیت لازم نبود: %s", exc)


async def _read(bot: Bot, settings: Settings, file, mime: str):
    image = (await bot.download(file)).read()
    extractor = gemini.make_extractor(settings.gemini_key)
    return await table_read.read_table(
        extractor, image, mime, settings.vision_models)


@router.callback_query(F.data == "dp:go")
async def on_start(cb: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    if active_admin(settings, cb.from_user.id) is None:
        await cb.answer()
        return
    if not settings.gemini_key:
        await cb.answer(t.READ_ERRORS["no_key"], show_alert=True)
        return
    await state.clear()
    await state.set_state(Daily.photos)
    await state.update_data(rows=[], photos=0)
    await cb.message.answer(t.ASK_PHOTOS, reply_markup=k.collect_kb())
    await cb.answer()


@router.message(Daily.photos, F.text)
async def on_text(message: Message) -> None:
    await message.answer(t.NEED_PHOTO)


@router.message(Daily.photos, F.photo)
@router.message(Daily.photos, F.document.mime_type.startswith("image/"))
async def on_photo(
    message: Message, state: FSMContext, settings: Settings, bot: Bot
) -> None:
    if active_admin(settings, message.from_user.id) is None:
        await state.clear()
        return
    file, mime = _image_of(message)
    if (file.file_size or 0) > MAX_BYTES:
        await message.answer(t.TOO_BIG)
        return
    async with _lock(message.from_user.id):
        data = await state.get_data()
        number = data.get("photos", 0) + 1
        await _show(bot, message, state, t.READING.format(
            n=number, rows=len(data["rows"])))
        status, rows = await _read(bot, settings, file, mime)
        if status != "ok":
            error = t.READ_ERRORS.get(status, t.READ_ERROR_GENERIC)
            await _show(bot, message, state, error)
            return
        total = daily_text.merge_rows(data["rows"], rows)
        await state.update_data(rows=total, photos=number)
        await _show(bot, message, state, t.GOT.format(
            photos=number, rows=len(total)))


@router.callback_query(Daily.photos, F.data == "dp:ok")
async def on_done(
    cb: CallbackQuery, state: FSMContext, settings: Settings, bot: Bot
) -> None:
    if active_admin(settings, cb.from_user.id) is None:
        await state.clear()
        await cb.answer()
        return
    async with _lock(cb.from_user.id):
        rows = (await state.get_data())["rows"]
        if not rows:
            await cb.message.answer(t.NOTHING)
            await cb.answer()
            return
        await daily_send.send_table(
            bot, cb.message.chat.id, rows, date.today().isoformat(),
            k.result_kb())
        await cb.message.edit_text(t.FINISHED.format(rows=len(rows)))
    await cb.answer()


@router.callback_query(F.data.in_({"dp:pic", "dp:vid"}))
async def on_soon(cb: CallbackQuery) -> None:
    await cb.answer(t.SOON, show_alert=True)


@router.callback_query(F.data == "dp:x")
async def on_cancel(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.message.answer(t.CANCELLED)
    await cb.answer()
