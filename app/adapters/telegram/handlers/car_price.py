"""Button 'car price': pick a brand group, then send that group's tables."""
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.adapters.telegram import daily_send, dbrun
from app.adapters.telegram.keyboards import car_price as k
from app.adapters.telegram.texts import car_price as t
from app.adapters.telegram.texts import daily_prices as dp
from app.adapters.telegram.texts import menu
from app.config import Settings
from app.core import brand_groups, brand_map, price_age, published_view
from app.data import repo_published

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")


def _ready(settings: Settings) -> tuple[dict | None, str | None]:
    """(data, note); data is None when unusable and note is the reply."""
    data = dbrun.run(settings, repo_published.get)
    if data is None or not data["rows"]:
        return None, t.SOON
    age = price_age.status(data["published_at"])
    if age == "expired":
        return None, t.EXPIRED
    return data, (t.OLD_NOTE if age == "old" else None)


async def _send(bot: Bot, chat_id: int, data: dict, rows: list[dict]) -> None:
    day_text, stamp = published_view.parts(data, dp)
    await daily_send.send_table(bot, chat_id, rows, day_text, None, stamp)


@router.message(F.text.in_((menu.BTN_CAR_PRICE, menu.BTN_CAR_PRICE_OLD)))
async def on_car_price(
    message: Message, settings: Settings, bot: Bot, state: FSMContext
) -> None:
    await state.clear()
    data, note = _ready(settings)
    if data is None:
        await message.answer(note)
        return
    if note:
        await message.answer(note)
    rows = data["rows"]
    if not brand_groups.has_brands(rows):
        await _send(bot, message.chat.id, data, rows)
        return
    items = brand_map.menu(rows, dp.BRAND_GROUPS)
    names = brand_map.names(dp.BRAND_GROUPS, dp.OTHER_BRAND)
    await message.answer(
        t.PICK_GROUP, reply_markup=k.groups_kb(items, names, t.BTN_GROUP, t.GROUP_STYLES))


@router.callback_query(F.data.regexp(r"^cp:g:\d+$"))
async def on_group(cb: CallbackQuery, settings: Settings, bot: Bot) -> None:
    data, note = _ready(settings)
    if data is None:
        await cb.answer(note, show_alert=True)
        return
    index = int(cb.data.split(":")[2])
    parts = brand_map.split(data["rows"], dp.BRAND_GROUPS)
    await cb.answer()
    if index < len(parts) and parts[index]:
        await _send(bot, cb.message.chat.id, data, parts[index])
