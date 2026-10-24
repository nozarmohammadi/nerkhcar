"""کیبوردهای ثبت قیمت از عکس (callback_data کوتاه)."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.adapters.telegram.texts import price_import as t


def _btn(text: str, data: str) -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton(text=text, callback_data=data)]


def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[_btn(t.BTN_CANCEL, "pi:x")])


def review_kb() -> InlineKeyboardMarkup:
    rows = [_btn(t.BTN_SAVE, "pi:ok"), _btn(t.BTN_CANCEL, "pi:x")]
    return InlineKeyboardMarkup(inline_keyboard=rows)
