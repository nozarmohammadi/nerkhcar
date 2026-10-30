"""Button 'technical specs': pick a brand group, a car, then show its specs."""
from functools import partial

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.adapters.telegram import dbrun
from app.adapters.telegram.keyboards import specs as k
from app.adapters.telegram.texts import menu
from app.adapters.telegram.texts import specs as t
from app.config import Settings
from app.adapters.telegram import specs_send
from app.core import specs_view
from app.data import repo_specs

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")


def _parts(settings: Settings) -> list[list[dict]]:
    rows = dbrun.run(settings, repo_specs.list_reviewed)
    return specs_view.split(rows, t.GROUPS)


@router.message(F.text == menu.BTN_SPECS)
async def on_specs(message: Message, settings: Settings, state: FSMContext) -> None:
    await state.clear()
    parts = _parts(settings)
    items = [(i, len(p)) for i, p in enumerate(parts) if p]
    if not items:
        await message.answer(t.SOON)
        return
    names = specs_view.names(t.GROUPS, t.OTHER)
    await message.answer(
        t.PICK_GROUP, reply_markup=k.groups_kb(items, names, t.BTN_GROUP))


@router.callback_query(F.data.regexp(r"^spec:g:\d+$"))
async def on_group(cb: CallbackQuery, settings: Settings) -> None:
    index = int(cb.data.split(":")[2])
    parts = _parts(settings)
    await cb.answer()
    if index < len(parts) and parts[index]:
        await cb.message.answer(t.PICK_CAR, reply_markup=k.cars_kb(parts[index]))


@router.callback_query(F.data.regexp(r"^spec:c:\d+$"))
async def on_car(cb: CallbackQuery, settings: Settings, bot: Bot) -> None:
    trim_id = int(cb.data.split(":")[2])
    row = dbrun.run(settings, partial(repo_specs.get, trim_id=trim_id))
    await cb.answer()
    if row is None:
        await cb.message.answer(t.MISSING)
        return
    title = t.TITLE.format(name=row["name"])
    pairs = specs_view.pairs(row["specs"], t.LABELS)
    theme = t.THEMES[specs_view.group_index(row["slug"], t.GROUPS)]
    await specs_send.send_table(
        bot, cb.message.chat.id, title, pairs, row["name"], theme,
        slug=row["slug"])
