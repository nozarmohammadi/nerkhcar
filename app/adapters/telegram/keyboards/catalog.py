"""کیبوردهای کاتالوگ (callback_data کوتاه با شناسهٔ عددی)."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.adapters.telegram.texts import catalog as c
from app.adapters.telegram.texts import price_import as pi


def _btn(text: str, data: str) -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton(text=text, callback_data=data)]


def _kb(rows: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=rows)


def brands_kb(brands: list[dict]) -> InlineKeyboardMarkup:
    rows = [_btn(b["name"], f"cat:b:{b['id']}") for b in brands]
    rows += [_btn(c.BTN_NEW_BRAND, "cat:nb"), _btn(c.BTN_BACK, "adm:panel")]
    return _kb(rows)


def models_kb(brand_id: int, models: list[dict]) -> InlineKeyboardMarkup:
    rows = [_btn(m["name"], f"cat:m:{m['id']}") for m in models]
    rows += [_btn(c.BTN_NEW_MODEL, f"cat:nm:{brand_id}"),
             _btn(pi.BTN_IMPORT, f"pi:{brand_id}"),
             _btn(c.BTN_BACK, "adm:cat")]
    return _kb(rows)


def trims_kb(model_id: int, brand_id: int) -> InlineKeyboardMarkup:
    return _kb([_btn(c.BTN_NEW_TRIM, f"cat:nt:{model_id}"),
                _btn(c.BTN_BACK, f"cat:b:{brand_id}")])


def cancel_kb() -> InlineKeyboardMarkup:
    return _kb([_btn(c.BTN_CANCEL, "cat:x")])
