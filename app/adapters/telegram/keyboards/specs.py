"""Keyboards of the 'technical specs' button (short numeric callback_data)."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.adapters.telegram.texts import specs as t
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



def detail_kb(trim_id: int, group: int, has_price: bool) -> InlineKeyboardMarkup:
    """Buttons under one car's specs: today's price (if any) and back."""
    rows = []
    if has_price:
        rows.append([InlineKeyboardButton(
            text=t.BTN_PRICE, callback_data=f"spec:p:{trim_id}")])
    rows.append([InlineKeyboardButton(
        text=t.BTN_BACK, callback_data=f"spec:g:{group}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_kb(group: int) -> InlineKeyboardMarkup:
    """Only the back button (used under the price message)."""
    return detail_kb(0, group, False)
