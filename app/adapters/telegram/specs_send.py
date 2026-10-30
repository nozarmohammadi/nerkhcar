"""Send one car's specs: cover + native table first, plain text if refused."""
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import (
    BufferedInputFile, InputMediaPhoto, InputRichMessage, InputRichMessageMedia,
)

from app.adapters.telegram.texts import specs as t
from app.core import brand_banner, daily_text, specs_html

log = logging.getLogger("nerkhcar")


def _rich(title: str, pairs: list, cover: str, theme: int) -> InputRichMessage:
    """Rich message: colored cover with the car name, then the table."""
    name = daily_text.fa(cover)
    key = brand_banner.banner_id(name)
    png = brand_banner.render(name, theme)
    media = InputRichMessageMedia(id=key, media=InputMediaPhoto(
        media=BufferedInputFile(png, f"{key}.png")))
    html = specs_html.build_html(title, pairs, t.HEAD, key)
    return InputRichMessage(html=html, is_rtl=True, media=[media])


async def send_table(
    bot: Bot, chat_id: int, title: str, pairs: list[tuple[str, str]],
    cover: str, theme: int,
) -> str:
    """Result: rich (native table) or text (fallback)."""
    try:
        await bot.send_rich_message(
            chat_id=chat_id, rich_message=_rich(title, pairs, cover, theme))
        return "rich"
    except TelegramAPIError as exc:
        log.warning("specs table not sent: %s", exc)
    await bot.send_message(
        chat_id=chat_id, text=specs_html.build_text(title, pairs))
    return "text"
