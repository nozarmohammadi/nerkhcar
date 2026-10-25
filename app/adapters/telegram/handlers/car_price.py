"""Button 'car price': send the last published daily table to any user."""
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.adapters.telegram import daily_send, dbrun
from app.adapters.telegram.texts import car_price as t
from app.adapters.telegram.texts import daily_prices as dp
from app.adapters.telegram.texts import menu
from app.config import Settings
from app.core import published_view
from app.data import repo_published

router = Router()
router.message.filter(F.chat.type == "private")


@router.message(F.text == menu.BTN_CAR_PRICE)
async def on_car_price(
    message: Message, settings: Settings, bot: Bot, state: FSMContext
) -> None:
    await state.clear()
    data = dbrun.run(settings, repo_published.get)
    if data is None or not data["rows"]:
        await message.answer(t.SOON)
        return
    day_text, stamp = published_view.parts(data, dp)
    await daily_send.send_table(
        bot, message.chat.id, data["rows"], day_text, None, stamp)
