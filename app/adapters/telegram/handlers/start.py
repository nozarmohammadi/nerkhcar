"""دستور /start."""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.adapters.telegram.keyboards.main_menu import main_menu
from app.adapters.telegram.texts import menu

router = Router()


@router.message(CommandStart())
async def on_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(menu.WELCOME, reply_markup=main_menu())
