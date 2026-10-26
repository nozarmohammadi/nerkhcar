"""Keyboards of the 'my car' form (short numeric callback_data)."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.adapters.telegram.texts import my_car as t
from app.core import model_lookup


def _btn(text: str, data: str) -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton(text=text, callback_data=data)]


def _nav(back: bool = True) -> list[list[InlineKeyboardButton]]:
    rows = [_btn(t.BTN_BACK, "mc:back")] if back else []
    return rows + [_btn(t.BTN_CANCEL, "mc:x")]


def models_kb(names: list[str], page: int) -> InlineKeyboardMarkup:
    rows = [_btn(name, f"mc:m:{i}") for i, name in model_lookup.page_of(names, page)]
    pages = model_lookup.page_count(names)
    move = []
    if page > 0:
        move.append(InlineKeyboardButton(text=t.BTN_PREV, callback_data=f"mc:p:{page - 1}"))
    if page < pages - 1:
        move.append(InlineKeyboardButton(text=t.BTN_NEXT, callback_data=f"mc:p:{page + 1}"))
    return InlineKeyboardMarkup(inline_keyboard=rows + ([move] if move else []) + _nav(False))


def years_kb(years: list[int]) -> InlineKeyboardMarkup:
    row = [InlineKeyboardButton(text=str(y), callback_data=f"mc:y:{y}") for y in years]
    rows = [row[i:i + 4] for i in range(0, len(row), 4)]
    return InlineKeyboardMarkup(inline_keyboard=rows + _nav())


def choice_kb(kind: str, labels: tuple) -> InlineKeyboardMarkup:
    rows = [_btn(label, f"mc:{kind}:{i}") for i, label in enumerate(labels)]
    return InlineKeyboardMarkup(inline_keyboard=rows + _nav())


def names_kb(found: list[str]) -> InlineKeyboardMarkup:
    """Search results: one button per name, by index."""
    rows = [_btn(n, f"mc:m:{i}") for i, n in enumerate(found)]
    return InlineKeyboardMarkup(inline_keyboard=rows + _nav(False))


def cancel_kb() -> InlineKeyboardMarkup:
    """Only the cancel button (typed steps)."""
    return InlineKeyboardMarkup(inline_keyboard=_nav(False))
