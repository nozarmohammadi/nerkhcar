"""کاتالوگ خودرو از پنل: برند ← مدل ← تیپ (هر ادمین فعال)."""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.adapters.telegram.guard import active_admin
from app.adapters.telegram.keyboards import catalog as k
from app.adapters.telegram.texts import catalog as c
from app.config import Settings
from app.core import catalog
from app.data import db, repo_catalog

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")

KINDS = {"nb": "brand", "nm": "model", "nt": "trim"}


class AddItem(StatesGroup):
    name = State()


def _run(settings: Settings, fn, *args):
    conn = db.connect(settings.db_path)
    try:
        return fn(conn, *args)
    finally:
        conn.close()


def _allowed(settings: Settings, uid: int) -> bool:
    return active_admin(settings, uid) is not None


def _brands_view(settings: Settings):
    brands = _run(settings, repo_catalog.list_brands)
    return c.BRANDS_TITLE, k.brands_kb(brands)


def _models_view(settings: Settings, brand_id: int):
    brand = _run(settings, repo_catalog.get_brand, brand_id)
    if brand is None:
        return None
    models = _run(settings, repo_catalog.list_models, brand_id)
    title = c.MODELS_TITLE.format(brand=brand["name"])
    return title, k.models_kb(brand_id, models)


def _trims_view(settings: Settings, model_id: int):
    model = _run(settings, repo_catalog.get_model, model_id)
    if model is None:
        return None
    trims = _run(settings, repo_catalog.list_trims, model_id)
    body = "\n".join(f"• {t['name']}" for t in trims) or c.EMPTY
    title = c.TRIMS_TITLE.format(model=model["name"]) + "\n" + body
    return title, k.trims_kb(model_id, model["brand_id"])


def _view_for(settings: Settings, kind: str, parent: int):
    if kind == "model":
        return _models_view(settings, parent)
    if kind == "trim":
        return _trims_view(settings, parent)
    return _brands_view(settings)


async def _show(cb: CallbackQuery, view) -> None:
    if view is None:
        await cb.answer(c.NOT_FOUND, show_alert=True)
        return
    await cb.message.edit_text(view[0], reply_markup=view[1])
    await cb.answer()


@router.callback_query(F.data == "adm:cat")
async def on_catalog(cb: CallbackQuery, settings: Settings) -> None:
    if not _allowed(settings, cb.from_user.id):
        await cb.answer()
        return
    await _show(cb, _brands_view(settings))


@router.callback_query(F.data.regexp(r"^cat:b:\d+$"))
async def on_brand(cb: CallbackQuery, settings: Settings) -> None:
    if not _allowed(settings, cb.from_user.id):
        await cb.answer()
        return
    await _show(cb, _models_view(settings, int(cb.data.split(":")[2])))


@router.callback_query(F.data.regexp(r"^cat:m:\d+$"))
async def on_model(cb: CallbackQuery, settings: Settings) -> None:
    if not _allowed(settings, cb.from_user.id):
        await cb.answer()
        return
    await _show(cb, _trims_view(settings, int(cb.data.split(":")[2])))


@router.callback_query(F.data.regexp(r"^cat:n[bmt](:\d+)?$"))
async def on_new(cb: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    if not _allowed(settings, cb.from_user.id):
        await cb.answer()
        return
    parts = cb.data.split(":")
    kind = KINDS[parts[1]]
    parent = int(parts[2]) if len(parts) > 2 else 0
    await state.set_state(AddItem.name)
    await state.update_data(kind=kind, parent=parent)
    await cb.message.answer(c.ASK_NAME[kind], reply_markup=k.cancel_kb())
    await cb.answer()


@router.callback_query(F.data == "cat:x")
async def on_cancel(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.message.answer(c.CANCELLED)
    await cb.answer()


@router.message(AddItem.name, F.text)
async def on_name(message: Message, state: FSMContext, settings: Settings) -> None:
    if not _allowed(settings, message.from_user.id):
        await state.clear()
        return
    data = await state.get_data()
    kind, parent = data["kind"], data["parent"]
    status = _run(settings, catalog.add_item, kind, parent, message.text)
    if status == "bad_name":
        await message.answer(c.BAD_NAME)
        return
    await state.clear()
    await message.answer(c.STATUS[status])
    view = _view_for(settings, kind, parent)
    if view:
        await message.answer(view[0], reply_markup=view[1])
