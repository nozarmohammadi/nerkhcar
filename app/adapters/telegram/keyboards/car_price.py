"""Keyboard of the 'car price' group picker (short numeric callback_data)."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core import daily_text



def groups_kb(
    items: list[tuple[int, int]], names: list[str], label: str,
    styles: tuple = ("primary",),
) -> InlineKeyboardMarkup:
    """items: (group index, row count); two buttons per line, one color."""
    buttons = [
        InlineKeyboardButton(
            text=label.format(name=names[i], n=daily_text.fa(n)),
            callback_data=f"cp:g:{i}", style=styles[min(i, len(styles) - 1)])
        for i, n in items
    ]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)
