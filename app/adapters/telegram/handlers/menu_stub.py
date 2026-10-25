"""جواب موقت دکمه‌های منو تا ساخته‌شدن منطق اصلی."""
from aiogram import F, Router
from aiogram.types import Message

from app.adapters.telegram.texts import menu

router = Router()
BUTTONS = {menu.BTN_FX_GOLD, menu.BTN_MY_CAR}


@router.message(F.text.in_(BUTTONS))
async def on_button(message: Message) -> None:
    await message.answer(menu.COMING_SOON)
