"""کیبورد منوی اصلی."""
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.adapters.telegram.texts import menu


def main_menu() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=menu.BTN_CAR_PRICE)],
        [KeyboardButton(text=menu.BTN_FX_GOLD)],
        [KeyboardButton(text=menu.BTN_MY_CAR)],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
