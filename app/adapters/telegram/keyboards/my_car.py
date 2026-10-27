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

def body_mode_kb(labels: tuple) -> InlineKeyboardMarkup:
    """Return body damage mode buttons."""
    return choice_kb("bm", labels)


def body_parts_kb(labels: tuple, selected: set[str]) -> InlineKeyboardMarkup:
    """Return toggle buttons for body parts."""
    rows = []
    for key, label in labels:
        mark = "✅ " if key in selected else "⬜ "
        rows.append(_btn(mark + label, f"mc:bp:{key}"))
    rows.append(_btn(t.BTN_CONFIRM, "mc:bp:done"))
    rows.extend(_nav())
    return InlineKeyboardMarkup(inline_keyboard=rows)


def color_kb(labels: tuple) -> InlineKeyboardMarkup:
    """Return color selection buttons."""
    return choice_kb("cl", tuple(label for _, label in labels))

def km_skip_kb() -> InlineKeyboardMarkup:
    """Return the optional mileage skip button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            _btn(t.BTN_KM_SKIP, "mc:km:skip"),
            _btn(t.BTN_CANCEL, "mc:x"),
        ]
    )
