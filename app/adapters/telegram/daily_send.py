"""فرستادن جدول قیمت روز: اول جدول بومی تلگرام، در صورت خطا متن فشرده."""
import logging
from datetime import datetime

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import (
    BufferedInputFile, InlineKeyboardMarkup, InputMediaPhoto,
    InputRichMessage, InputRichMessageMedia,
)

from app.adapters.telegram.texts import daily_prices as t
from app.core import brand_banner, brand_map, daily_text

log = logging.getLogger("nerkhcar")


async def _send_text(
    bot: Bot, chat_id: int, rows: list[dict], date: str, markup
) -> None:
    chunks = daily_text.text_chunks(daily_text.build_text(rows, date, t))
    for i, chunk in enumerate(chunks):
        last = i == len(chunks) - 1
        await bot.send_message(
            chat_id=chat_id, text=chunk, reply_markup=markup if last else None)


def _rich(html: str, rows: list[dict]) -> InputRichMessage:
    """Rich message carrying the brand banner images this html uses."""
    order = tuple(brand_map.names(t.BRAND_GROUPS, t.OTHER_BRAND))
    banners = brand_banner.banners_in(html, rows, t.OTHER_BRAND, order)
    media = [
        InputRichMessageMedia(id=key, media=InputMediaPhoto(
            media=BufferedInputFile(png, f"{key}.png")))
        for key, png in banners.items()
    ]
    return InputRichMessage(html=html, is_rtl=True, media=media or None)


async def send_table(
    bot: Bot, chat_id: int, rows: list[dict], date: str,
    markup: InlineKeyboardMarkup | None, now: datetime | None = None,
) -> str:
    """نتیجه: rich (جدول بومی) یا text (متن فشرده)."""
    rows = brand_map.regroup(rows, t.BRAND_GROUPS, t.OTHER_BRAND)
    parts = daily_text.build_html_chunks(rows, date, t, now)
    try:
        for i, html in enumerate(parts):
            last = i == len(parts) - 1
            await bot.send_rich_message(
                chat_id=chat_id, reply_markup=markup if last else None,
                rich_message=_rich(html, rows))
        return "rich"
    except TelegramAPIError as exc:
        log.warning("جدول بومی فرستاده نشد: %s", exc)
    await _send_text(bot, chat_id, rows, date, markup)
    return "text"
