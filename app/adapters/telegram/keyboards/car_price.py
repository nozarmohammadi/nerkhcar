"""Keyboards of the daily price button: brand list and back button."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.adapters.telegram.texts import car_price as t
from app.core import daily_text

PER_ROW = 2


def _label(name: str, count: int) -> str:
    return t.BRAND_BTN.format(name=name or t.OTHER_BRAND, n=daily_text.fa(count))


def brands_kb(brands: list[tuple[str, int]]) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=_label(name, count), callback_data=f"cp:b:{i}")
        for i, (name, count) in enumerate(brands)
    ]
    rows = [buttons[i:i + PER_ROW] for i in range(0, len(buttons), PER_ROW)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_kb() -> InlineKeyboardMarkup:
    button = InlineKeyboardButton(text=t.BTN_BACK, callback_data="cp:back")
    return InlineKeyboardMarkup(inline_keyboard=[[button]])
