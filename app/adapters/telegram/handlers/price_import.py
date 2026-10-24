"""ثبت مرجع قیمت از عکس: منبع ← عکس ← پیش‌نویس ← ویرایش ← ذخیره."""
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.adapters.ai import gemini
from app.adapters.telegram import draft_view
from app.adapters.telegram.dbrun import run
from app.adapters.telegram.guard import active_admin
from app.adapters.telegram.keyboards import price_import as k
from app.adapters.telegram.texts import price_import as t
from app.config import Settings
from app.core import catalog, edit_command, ref_import, table_read
from app.data import repo_catalog

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")
MAX_BYTES = 8 * 1024 * 1024


class PriceImport(StatesGroup):
    source = State()
    photo = State()
    review = State()


def _image_of(message: Message):
    if message.photo:
        return message.photo[-1], "image/jpeg"
    return message.document, message.document.mime_type


async def _send_draft(message: Message, rows: list[dict], source: str) -> None:
    for text in draft_view.draft_chunks(rows, source):
        await message.answer(text)
    await message.answer(t.HELP, reply_markup=k.review_kb())


@router.callback_query(F.data.regexp(r"^pi:\d+$"))
async def on_start(cb: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    if active_admin(settings, cb.from_user.id) is None:
        await cb.answer()
        return
    brand_id = int(cb.data.split(":")[1])
    if not settings.gemini_key:
        await cb.answer(t.NO_KEY, show_alert=True)
        return
    if run(settings, repo_catalog.get_brand, brand_id) is None:
        await cb.answer(t.NO_BRAND, show_alert=True)
        return
    await state.clear()
    await state.set_state(PriceImport.source)
    await state.update_data(brand_id=brand_id)
    await cb.message.answer(t.ASK_SOURCE, reply_markup=k.cancel_kb())
    await cb.answer()


@router.message(PriceImport.source, F.text)
async def on_source(message: Message, state: FSMContext, settings: Settings) -> None:
    if active_admin(settings, message.from_user.id) is None:
        await state.clear()
        return
    name = catalog.clean_name(message.text)
    if name is None:
        await message.answer(t.BAD_SOURCE)
        return
    await state.update_data(source=name)
    await state.set_state(PriceImport.photo)
    await message.answer(t.ASK_PHOTO, reply_markup=k.cancel_kb())


@router.message(PriceImport.photo, F.text)
async def on_need_photo(message: Message) -> None:
    await message.answer(t.NEED_PHOTO)


@router.message(PriceImport.photo, F.photo)
@router.message(PriceImport.photo, F.document.mime_type.startswith("image/"))
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
    await state.update_data(rows=rows)
    await state.set_state(PriceImport.review)
    await _send_draft(message, rows, (await state.get_data())["source"])


@router.message(PriceImport.review, F.text)
async def on_edit(message: Message, state: FSMContext, settings: Settings) -> None:
    if active_admin(settings, message.from_user.id) is None:
        await state.clear()
        return
    parsed = edit_command.parse_edit(message.text, t.KEYWORDS)
    if parsed is None:
        await message.answer(t.BAD_COMMAND)
        return
    data = await state.get_data()
    status = ref_import.apply_edit(data["rows"], *parsed)
    if status != "ok":
        await message.answer(t.EDIT_ERRORS[status])
        return
    await _send_draft(message, data["rows"], data["source"])


@router.callback_query(PriceImport.review, F.data == "pi:ok")
async def on_confirm(cb: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    admin = active_admin(settings, cb.from_user.id)
    if admin is None:
        await state.clear()
        await cb.answer()
        return
    data = await state.get_data()
    status, saved, blocked = run(
        settings, ref_import.save_references, data["rows"], data["brand_id"],
        data["source"], admin.tg_id, t.DEFAULT_TRIM)
    if status == "nothing":
        await cb.message.answer(t.NOTHING_READY)
    elif status == "ok":
        await state.set_state(PriceImport.photo)
        text = t.SAVED.format(saved=saved, blocked=blocked) + "\n" + t.NEXT_PHOTO
        await cb.message.answer(text, reply_markup=k.cancel_kb())
    else:
        await state.clear()
        await cb.message.answer(t.NO_BRAND)
    await cb.answer()


@router.callback_query(F.data == "pi:x")
async def on_cancel(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.message.answer(t.CANCELLED)
    await cb.answer()
