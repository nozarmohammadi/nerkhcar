"""Send one car's specs: cover, photo slideshow and native table; text if refused."""
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import (
    BufferedInputFile, InputMediaPhoto, InputRichMessage, InputRichMessageMedia,
)

from app.adapters.telegram.texts import specs as t
from app.core import brand_banner, car_images, daily_text, specs_html

log = logging.getLogger("nerkhcar")


def _media(key: str, data: bytes, filename: str) -> InputRichMessageMedia:
    photo = InputMediaPhoto(media=BufferedInputFile(data, filename))
    return InputRichMessageMedia(id=key, media=photo)


def _rich(
    title: str, pairs: list, cover: str, theme: int, photos: list | tuple = ()
) -> InputRichMessage:
    """Rich message: colored cover, optional photo slideshow, then the table."""
    name = daily_text.fa(cover)
    key = brand_banner.banner_id(name)
    media = [_media(key, brand_banner.render(name, theme), f"{key}.png")]
    ids = []
    for n, data in enumerate(photos, 1):
        ids.append(f"ph{n}")
        media.append(_media(ids[-1], data, f"{ids[-1]}.jpg"))
    html = specs_html.build_html(title, pairs, t.HEAD, key, tuple(ids))
    return InputRichMessage(html=html, is_rtl=True, media=media)


async def _try_rich(bot: Bot, chat_id: int, rich: InputRichMessage) -> bool:
    try:
        await bot.send_rich_message(chat_id=chat_id, rich_message=rich)
        return True
    except TelegramAPIError as exc:
        log.warning("specs table not sent: %s", exc)
        return False


async def send_table(
    bot: Bot, chat_id: int, title: str, pairs: list[tuple[str, str]],
    cover: str, theme: int, slug: str = "",
) -> str:
    """Result: rich (native table) or text (fallback). Photos are optional."""
    photos = car_images.load(slug) if slug else []
    for use in ([photos, []] if photos else [[]]):
        if await _try_rich(bot, chat_id, _rich(title, pairs, cover, theme, use)):
            return "rich"
    await bot.send_message(
        chat_id=chat_id, text=specs_html.build_text(title, pairs))
    return "text"
