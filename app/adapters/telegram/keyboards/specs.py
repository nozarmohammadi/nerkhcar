"""Keyboards of the 'technical specs' button (short numeric callback_data)."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core import daily_text

# Telegram allows at most 100 buttons in one inline keyboard.
MAX_BUTTONS = 99


def groups_kb(
    items: list[tuple[int, int]], names: list[str], label: str
) -> InlineKeyboardMarkup:
    """items: (group index, car count); two buttons per line."""
    buttons = [
        InlineKeyboardButton(
            text=label.format(name=names[i], n=daily_text.fa(n)),
            callback_data=f"spec:g:{i}")
        for i, n in items
    ]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def cars_kb(rows: list[dict]) -> InlineKeyboardMarkup:
    """One button per car; callback_data carries the trim id."""
    buttons = [
        [InlineKeyboardButton(
            text=r["name"], callback_data=f"spec:c:{r['trim_id']}")]
        for r in rows[:MAX_BUTTONS]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
