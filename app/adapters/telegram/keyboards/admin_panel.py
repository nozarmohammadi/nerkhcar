"""کیبوردهای پنل ادمین (callback_data کوتاه با شناسهٔ عددی)."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.adapters.telegram.texts import admin_panel as p
from app.adapters.telegram.texts import daily_prices as dp


def _btn(text: str, data: str) -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton(text=text, callback_data=data)]


def panel_kb(role: str) -> InlineKeyboardMarkup:
    rows = [_btn(p.BTN_CATALOG, "adm:cat"), _btn(dp.BTN_DAILY, "dp:go")]
    if role == "owner":
        owner_rows = [_btn(p.BTN_ADMINS, "adm:menu"), _btn(p.BTN_LOG, "adm:log")]
        rows = owner_rows + rows
    return InlineKeyboardMarkup(inline_keyboard=rows)


def manage_kb() -> InlineKeyboardMarkup:
    rows = [
        _btn(p.BTN_ADD, "adm:add"),
        _btn(p.BTN_LIST, "adm:list"),
        _btn(p.BTN_REMOVE, "adm:rm"),
        _btn(p.BTN_RESET, "adm:rs"),
        _btn(p.BTN_BACK, "adm:panel"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def pick_kb(action: str, admins: list[dict]) -> InlineKeyboardMarkup:
    rows = [_btn(str(a["tg_id"]), f"adm:{action}:{a['tg_id']}") for a in admins]
    return InlineKeyboardMarkup(inline_keyboard=rows)
