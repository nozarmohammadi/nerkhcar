"""قیمت روز خودرو: چند عکس ← خواندن ← جمع‌کردن ← خروجی متن."""
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.adapters.ai import gemini
from app.adapters.telegram.guard import active_admin
from app.adapters.telegram.keyboards import daily_prices as k
from app.adapters.telegram.texts import daily_prices as t
from app.config import Settings
from app.core import daily_text, table_read

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")
MAX_BYTES = 8 * 1024 * 1024


class Daily(StatesGroup):
    photos = State()


def _image_of(message: Message):
    if message.photo:
        return message.photo[-1], "image/jpeg"
    return message.document, message.document.mime_type


def _today() -> str:
    from datetime import date
    return date.today().isoformat()


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
    await state.update_data(rows=[])
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
    await message.answer(t.READING)
    image = (await bot.download(file)).read()
    extractor = gemini.make_extractor(settings.gemini_key)
    status, rows = await table_read.read_table(
        extractor, image, mime, settings.vision_models)
    if status != "ok":
        await message.answer(t.READ_ERRORS.get(status, t.READ_ERROR_GENERIC))
        return
    data = await state.get_data()
    total = daily_text.merge_rows(data["rows"], rows)
    await state.update_data(rows=total)
    await message.answer(
        t.GOT_ROWS.format(count=len(rows), total=len(total)),
        reply_markup=k.collect_kb())


@router.callback_query(Daily.photos, F.data == "dp:ok")
async def on_done(cb: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    if active_admin(settings, cb.from_user.id) is None:
        await state.clear()
        await cb.answer()
        return
    rows = (await state.get_data())["rows"]
    if not rows:
        await cb.message.answer(t.NOTHING)
        await cb.answer()
        return
    text = daily_text.build_text(rows, _today(), t)
    await cb.message.answer(text, reply_markup=k.result_kb())
    await cb.answer()


@router.callback_query(F.data.in_({"dp:pic", "dp:vid"}))
async def on_soon(cb: CallbackQuery) -> None:
    await cb.answer(t.SOON, show_alert=True)


@router.callback_query(F.data == "dp:x")
async def on_cancel(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.message.answer(t.CANCELLED)
    await cb.answer()
