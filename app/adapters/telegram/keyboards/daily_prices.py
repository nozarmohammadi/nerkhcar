"""کیبوردهای قیمت روز خودرو."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.adapters.telegram.texts import daily_prices as t


def _btn(text: str, data: str) -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton(text=text, callback_data=data)]


def collect_kb() -> InlineKeyboardMarkup:
    rows = [_btn(t.BTN_DONE, "dp:ok"), _btn(t.BTN_CANCEL, "dp:x")]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def result_kb() -> InlineKeyboardMarkup:
    rows = [_btn(t.BTN_PIC, "dp:pic"), _btn(t.BTN_VIDEO, "dp:vid")]
    return InlineKeyboardMarkup(inline_keyboard=rows)
