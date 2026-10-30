"""Send one car's specs: native table first, plain text if Telegram refuses."""
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import InputRichMessage

from app.adapters.telegram.texts import specs as t
from app.core import specs_html

log = logging.getLogger("nerkhcar")


async def send_table(
    bot: Bot, chat_id: int, title: str, pairs: list[tuple[str, str]]
) -> str:
    """Result: rich (native table) or text (fallback)."""
    html = specs_html.build_html(title, pairs, t.HEAD, t.FOOT)
    try:
        await bot.send_rich_message(
            chat_id=chat_id, rich_message=InputRichMessage(html=html, is_rtl=True))
        return "rich"
    except TelegramAPIError as exc:
        log.warning("specs table not sent: %s", exc)
    await bot.send_message(
        chat_id=chat_id, text=specs_html.build_text(title, pairs, t.FOOT))
    return "text"
