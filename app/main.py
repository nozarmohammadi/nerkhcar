"""فقط راه‌اندازی ربات."""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent

from app.adapters.telegram.handlers import (
    admin_audit, admin_catalog, admin_login, admin_manage, admin_panel,
    car_price, daily_image, daily_prices, daily_resume, daily_video,
    fx_price, menu_stub, music_upload, my_car, price_import, specs, start,
)
from app.adapters.telegram.texts import menu
from app.adapters.telegram.texts import error_alert as alert_texts
from app.adapters.telegram.throttle import ThrottleMiddleware
from app.core.error_alert import ErrorAlertGate
from app.config import Settings, load_settings
from app.data import db, repo_admins, repo_audit
from app.jobs import car_price_job
from app.logging_setup import setup_logging

log = logging.getLogger("nerkhcar")
_ALERT_GATE = ErrorAlertGate()

# ترتیب مهم است: menu_stub باید آخر باشد
ROUTER_MODULES = (
    start, music_upload, admin_login, admin_panel, admin_manage, admin_audit,
    admin_catalog, price_import, daily_prices, daily_image, daily_video,
    daily_resume, car_price, fx_price, my_car, specs, menu_stub,
)


async def on_error(event: ErrorEvent, bot=None, settings=None) -> bool:
    kind = type(event.exception).__name__
    log.error("خطای پیش‌بینی‌نشده: %s", kind)
    message = event.update.message
    if message:
        await message.answer(menu.ERROR_GENERIC)
    if bot is not None and settings is not None and _ALERT_GATE.allow():
        try:
            await bot.send_message(
                settings.owner_id, alert_texts.OWNER_ERROR.format(kind=kind)
            )
        except Exception as exc:
            log.warning("owner error alert failed: %s", type(exc).__name__)
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
    owner = getattr(settings, "owner_id", None)
    throttle = ThrottleMiddleware(exempt_ids=(owner,) if owner else ())
    dp.message.outer_middleware(throttle)
    dp.callback_query.outer_middleware(throttle)
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
    price_task = asyncio.create_task(car_price_job.loop(settings, bot))
    await build_dispatcher(settings).start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
