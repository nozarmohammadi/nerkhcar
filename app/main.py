"""فقط راه‌اندازی ربات."""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent

from app.adapters.telegram.handlers import (
    admin_audit, admin_catalog, admin_login, admin_manage, admin_panel,
    daily_prices, menu_stub, price_import, start,
)
from app.adapters.telegram.texts import menu
from app.config import Settings, load_settings
from app.data import db, repo_admins, repo_audit
from app.logging_setup import setup_logging

log = logging.getLogger("nerkhcar")

# ترتیب مهم است: menu_stub باید آخر باشد
ROUTER_MODULES = (
    start, admin_login, admin_panel, admin_manage, admin_audit,
    admin_catalog, price_import, daily_prices, menu_stub,
)


async def on_error(event: ErrorEvent) -> bool:
    log.error("خطای پیش‌بینی‌نشده: %s", type(event.exception).__name__)
    message = event.update.message
    if message:
        await message.answer(menu.ERROR_GENERIC)
    return True


def prepare_db(settings: Settings) -> None:
    db.migrate(settings.db_path, settings.db_path.parent.parent / "backups")
    conn = db.connect(settings.db_path)
    try:
        if repo_admins.ensure_owner(conn, settings.owner_id):
            repo_audit.add_entry(conn, None, "owner_created")
    finally:
        conn.close()


def build_dispatcher(settings: Settings) -> Dispatcher:
    dp = Dispatcher(settings=settings)
    for module in ROUTER_MODULES:
        dp.include_router(module.router)
    dp.errors.register(on_error)
    return dp


async def main() -> None:
    settings = load_settings()
    setup_logging(settings.log_dir)
    prepare_db(settings)
    bot = Bot(token=settings.bot_token)
    log.info("ربات در حال شروع است")
    await build_dispatcher(settings).start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
