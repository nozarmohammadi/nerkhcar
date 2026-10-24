"""فقط راه‌اندازی ربات."""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent

from app.adapters.telegram.handlers import menu_stub, start
from app.adapters.telegram.texts import menu
from app.config import load_settings
from app.logging_setup import setup_logging

log = logging.getLogger("nerkhcar")


async def on_error(event: ErrorEvent) -> bool:
    log.error("خطای پیش‌بینی‌نشده: %s", type(event.exception).__name__)
    message = event.update.message
    if message:
        await message.answer(menu.ERROR_GENERIC)
    return True


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(menu_stub.router)
    dp.errors.register(on_error)
    return dp


async def main() -> None:
    settings = load_settings()
    setup_logging(settings.log_dir)
    bot = Bot(token=settings.bot_token)
    log.info("ربات در حال شروع است")
    await build_dispatcher().start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
