"""Button 'FX, coin and gold': send fresh prices to any user."""
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.adapters.telegram import fx_refresh, fx_send
from app.adapters.telegram.texts import fx as t
from app.adapters.telegram.texts import menu
from app.config import Settings

router = Router()
router.message.filter(F.chat.type == "private")


@router.message(F.text == menu.BTN_FX_GOLD)
async def on_fx(
    message: Message, settings: Settings, bot: Bot, state: FSMContext
) -> None:
    await state.clear()
    rows = await fx_refresh.get_rows(settings)
    if not rows:
        await message.answer(t.SOON)
        return
    await fx_send.send_table(bot, message.chat.id, rows)
