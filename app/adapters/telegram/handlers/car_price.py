"""Button 'car price': brand list first, then the table of the chosen brand."""
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.adapters.telegram import daily_send, dbrun
from app.adapters.telegram.keyboards import car_price as kb
from app.adapters.telegram.texts import car_price as t
from app.adapters.telegram.texts import daily_prices as dp
from app.adapters.telegram.texts import menu
from app.config import Settings
from app.core import brand_groups, price_age, published_view
from app.data import repo_published

router = Router()
router.message.filter(F.chat.type == "private")


async def _published(settings: Settings, message: Message) -> dict | None:
    """Load the published table; answer and return None when unusable."""
    data = dbrun.run(settings, repo_published.get)
    if data is None or not data["rows"]:
        await message.answer(t.SOON)
        return None
    age = price_age.status(data["published_at"])
    if age == "expired":
        await message.answer(t.EXPIRED)
        return None
    if age == "old":
        await message.answer(t.OLD_NOTE)
    return data


async def _send(bot: Bot, chat_id: int, data: dict, rows: list, markup) -> None:
    day_text, stamp = published_view.parts(data, dp)
    await daily_send.send_table(bot, chat_id, rows, day_text, markup, stamp)


async def _ask_brand(message: Message, rows: list) -> None:
    brands = brand_groups.brand_list(rows)
    await message.answer(t.PICK_BRAND, reply_markup=kb.brands_kb(brands))


@router.message(F.text == menu.BTN_CAR_PRICE)
async def on_car_price(
    message: Message, settings: Settings, bot: Bot, state: FSMContext
) -> None:
    await state.clear()
    data = await _published(settings, message)
    if data is None:
        return
    if not brand_groups.has_brands(data["rows"]):
        await _send(bot, message.chat.id, data, data["rows"], None)
        return
    await _ask_brand(message, data["rows"])


@router.callback_query(F.data.startswith("cp:b:"))
async def on_brand(cb: CallbackQuery, settings: Settings, bot: Bot) -> None:
    await cb.answer()
    data = await _published(settings, cb.message)
    if data is None:
        return
    rows = brand_groups.rows_of(data["rows"], int(cb.data.split(":")[2]))
    if not rows:
        await _ask_brand(cb.message, data["rows"])
        return
    brand = rows[0].get("brand") or t.OTHER_BRAND
    await cb.message.answer(t.BRAND_TITLE.format(brand=brand))
    await _send(bot, cb.message.chat.id, data, rows, kb.back_kb())


@router.callback_query(F.data == "cp:back")
async def on_back(cb: CallbackQuery, settings: Settings) -> None:
    await cb.answer()
    data = await _published(settings, cb.message)
    if data is not None:
        await _ask_brand(cb.message, data["rows"])
