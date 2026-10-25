"""Admin command /music: upload the background music of the price video."""
import asyncio
import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.adapters import music_store
from app.adapters.telegram.guard import active_admin
from app.adapters.telegram.texts import music as t
from app.config import Settings

log = logging.getLogger("nerkhcar")
router = Router()
router.message.filter(F.chat.type == "private")
MAX_BYTES = 8 * 1024 * 1024


class Music(StatesGroup):
    waiting = State()


@router.message(Command("music"))
async def on_music(
    message: Message, state: FSMContext, settings: Settings
) -> None:
    if active_admin(settings, message.from_user.id) is None:
        return
    await state.set_state(Music.waiting)
    await message.answer(t.ASK)


async def _store(message: Message, state: FSMContext, data: bytes) -> None:
    try:
        seconds = await asyncio.to_thread(music_store.save_music, data)
    except music_store.MusicError:
        await message.answer(t.BAD_FILE)
        return
    except OSError:
        log.exception("music save failed")
        await message.answer(t.FAILED)
        return
    await state.clear()
    log.info("music saved: %d seconds", int(seconds))
    await message.answer(t.SAVED.format(sec=int(seconds), kb=len(data) // 1024))


@router.message(Music.waiting)
async def on_file(
    message: Message, state: FSMContext, bot: Bot, settings: Settings
) -> None:
    if active_admin(settings, message.from_user.id) is None:
        await state.clear()
        return
    file = message.audio or message.document or message.voice
    if file is None:
        await message.answer(t.NEED_AUDIO)
        return
    if (file.file_size or 0) > MAX_BYTES:
        await message.answer(t.TOO_BIG)
        return
    data = (await bot.download(file)).read()
    await _store(message, state, data)
