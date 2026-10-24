"""نمایش لاگ ممیزی (فقط مالک)."""
from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.adapters.telegram.guard import owner_only
from app.adapters.telegram.texts import admin_panel as p
from app.config import Settings
from app.core import audit_view
from app.data import db

router = Router()
router.callback_query.filter(F.message.chat.type == "private")


def _load(settings: Settings) -> list[dict]:
    conn = db.connect(settings.db_path)
    try:
        return audit_view.recent_rows(conn)
    finally:
        conn.close()


def _format(rows: list[dict]) -> str:
    if not rows:
        return p.LOG_EMPTY
    lines = [
        p.LOG_ROW.format(
            at=r["at"], who=r["who"],
            action=p.ACTION_LABELS.get(r["action"], r["action"]),
            detail=r["detail"],
        ).rstrip()
        for r in rows
    ]
    return p.LOG_TITLE + "\n\n" + "\n".join(lines)


@router.callback_query(F.data == "adm:log")
async def on_log(cb: CallbackQuery, settings: Settings) -> None:
    if owner_only(settings, cb.from_user.id) is None:
        await cb.answer()
        return
    await cb.message.answer(_format(_load(settings)))
    await cb.answer()
