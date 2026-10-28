"""مدیریت ادمین‌ها از پنل (فقط مالک)."""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.adapters.telegram.guard import owner_only, deny
from app.adapters.telegram.keyboards.admin_panel import pick_kb
from app.adapters.telegram.texts import admin_panel as p
from app.config import Settings
from app.core import admin_manage as manage
from app.data import db, repo_admins

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")


class AddAdmin(StatesGroup):
    ask_id = State()


def _run(settings: Settings, fn, *args):
    conn = db.connect(settings.db_path)
    try:
        return fn(conn, *args)
    finally:
        conn.close()


@router.callback_query(F.data == "adm:add")
async def on_add(cb: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    if owner_only(settings, cb.from_user.id) is None:
        await deny(cb, settings)
        return
    await state.set_state(AddAdmin.ask_id)
    await cb.message.answer(p.ASK_ID)
    await cb.answer()


@router.message(AddAdmin.ask_id, F.text)
async def on_new_id(message: Message, state: FSMContext, settings: Settings) -> None:
    actor = owner_only(settings, message.from_user.id)
    if actor is None:
        await state.clear()
        return
    text = message.text.strip()
    if not text.isdigit() or len(text) > 15:
        await message.answer(p.BAD_ID)
        return
    status, temp = _run(settings, manage.add_editor, actor, int(text))
    await state.clear()
    await message.answer(p.ADDED.format(pw=temp) if status == "ok" else p.STATUS[status])


@router.callback_query(F.data == "adm:list")
async def on_list(cb: CallbackQuery, settings: Settings) -> None:
    if owner_only(settings, cb.from_user.id) is None:
        await deny(cb, settings)
        return
    lines = [
        p.LIST_ROW.format(
            uid=r["tg_id"], role=r["role"],
            state=p.STATE_ON if r["is_active"] else p.STATE_OFF,
        )
        for r in _run(settings, repo_admins.list_admins)
    ]
    await cb.message.answer("\n".join(lines))
    await cb.answer()


async def _pick(cb: CallbackQuery, settings: Settings, action: str, title: str) -> None:
    if owner_only(settings, cb.from_user.id) is None:
        await cb.answer()
        return
    rows = [r for r in _run(settings, repo_admins.list_admins)
            if r["role"] == "editor" and r["is_active"]]
    if not rows:
        await cb.answer(p.NO_EDITORS, show_alert=True)
        return
    await cb.message.answer(title, reply_markup=pick_kb(action, rows))
    await cb.answer()


@router.callback_query(F.data == "adm:rm")
async def on_pick_remove(cb: CallbackQuery, settings: Settings) -> None:
    await _pick(cb, settings, "rm", p.PICK_REMOVE)


@router.callback_query(F.data == "adm:rs")
async def on_pick_reset(cb: CallbackQuery, settings: Settings) -> None:
    await _pick(cb, settings, "rs", p.PICK_RESET)


@router.callback_query(F.data.regexp(r"^adm:rm:\d+$"))
async def on_remove(cb: CallbackQuery, settings: Settings) -> None:
    actor = owner_only(settings, cb.from_user.id)
    if actor is None:
        await deny(cb, settings)
        return
    status = _run(settings, manage.remove_admin, actor, int(cb.data.split(":")[2]))
    await cb.message.answer(p.STATUS[status])
    await cb.answer()


@router.callback_query(F.data.regexp(r"^adm:rs:\d+$"))
async def on_reset(cb: CallbackQuery, settings: Settings) -> None:
    actor = owner_only(settings, cb.from_user.id)
    if actor is None:
        await deny(cb, settings)
        return
    status, temp = _run(settings, manage.reset_password, actor,
                        int(cb.data.split(":")[2]))
    await cb.message.answer(p.RESET_DONE.format(pw=temp) if status == "ok" else p.STATUS[status])
    await cb.answer()
