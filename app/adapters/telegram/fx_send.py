"""Send the FX table: native table first, plain text if Telegram refuses."""
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import InputRichMessage

from app.adapters.telegram.texts import daily_prices as dp
from app.adapters.telegram.texts import fx as t
from app.core import daily_text, fx_view, published_view

log = logging.getLogger("nerkhcar")


def _day_line(rows: list[dict]) -> str:
    stamp = fx_view.oldest_stamp(rows)
    day_text, local = published_view.parts({"published_at": stamp}, dp)
    return dp.DATE_LINE.format(
        date=day_text, time=daily_text.time_text(dp, local))


async def send_table(bot: Bot, chat_id: int, rows: list[dict]) -> str:
    """Result: rich (native table) or text (fallback)."""
    line = _day_line(rows)
    html = fx_view.build_html(rows, line, t)
    try:
        await bot.send_rich_message(
            chat_id=chat_id, rich_message=InputRichMessage(html=html, is_rtl=True))
        return "rich"
    except TelegramAPIError as exc:
        log.warning("fx table not sent: %s", exc)
    await bot.send_message(chat_id=chat_id, text=fx_view.build_text(rows, line, t))
    return "text"
