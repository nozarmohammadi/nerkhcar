"""فرستادن جدول قیمت روز: اول جدول بومی تلگرام، در صورت خطا متن فشرده."""
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import InlineKeyboardMarkup, InputRichMessage

from app.adapters.telegram.texts import daily_prices as t
from app.core import daily_text

log = logging.getLogger("nerkhcar")


async def _send_text(
    bot: Bot, chat_id: int, rows: list[dict], date: str, markup
) -> None:
    chunks = daily_text.text_chunks(daily_text.build_text(rows, date, t))
    for i, chunk in enumerate(chunks):
        last = i == len(chunks) - 1
        await bot.send_message(
            chat_id=chat_id, text=chunk, reply_markup=markup if last else None)


async def send_table(
    bot: Bot, chat_id: int, rows: list[dict], date: str,
    markup: InlineKeyboardMarkup | None,
) -> str:
    """نتیجه: rich (جدول بومی) یا text (متن فشرده)."""
    html = daily_text.build_html(rows, date, t)
    try:
        await bot.send_rich_message(
            chat_id=chat_id, reply_markup=markup,
            rich_message=InputRichMessage(html=html, is_rtl=True))
        return "rich"
    except TelegramAPIError as exc:
        log.warning("جدول بومی فرستاده نشد: %s", exc)
    await _send_text(bot, chat_id, rows, date, markup)
    return "text"
