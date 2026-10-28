"""منوی اصلی پنل ادمین."""
from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.adapters.telegram.guard import active_admin, deny, owner_only
from app.adapters.telegram.keyboards.admin_panel import manage_kb, panel_kb
from app.adapters.telegram.texts import admin_panel as p
from app.config import Settings

router = Router()
router.callback_query.filter(F.message.chat.type == "private")


@router.callback_query(F.data == "adm:panel")
async def on_panel(cb: CallbackQuery, settings: Settings) -> None:
    admin = active_admin(settings, cb.from_user.id)
    if admin is None:
        await deny(cb, settings)
        return
    await cb.message.edit_text(p.PANEL_TITLE, reply_markup=panel_kb(admin.role))
    await cb.answer()


@router.callback_query(F.data == "adm:menu")
async def on_menu(cb: CallbackQuery, settings: Settings) -> None:
    if owner_only(settings, cb.from_user.id) is None:
        await deny(cb, settings)
        return
    await cb.message.edit_text(p.ADMINS_TITLE, reply_markup=manage_kb())
    await cb.answer()
