"""Daily prices: entry point, resume and restart of today's saved draft."""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.adapters.telegram import daily_draft
from app.adapters.telegram.guard import active_admin
from app.adapters.telegram.handlers.daily_state import Daily
from app.adapters.telegram.keyboards import daily_prices as k
from app.adapters.telegram.texts import daily_prices as t
from app.config import Settings
from app.core import daily_text

router = Router()
router.callback_query.filter(F.message.chat.type == "private")


async def _open(
    cb: CallbackQuery, state: FSMContext, settings: Settings,
    draft: dict | None = None,
) -> None:
    """Put the admin into the photo-collecting state (new or resumed draft)."""
    fresh = draft is None
    if fresh:
        draft = {"id": daily_draft.start(settings, cb.from_user.id),
                 "photos": 0, "rows": []}
    await state.clear()
    await state.set_state(Daily.photos)
    await state.update_data(
        rows=draft["rows"], photos=draft["photos"], batch_id=draft["id"])
    if fresh:
        await cb.message.answer(t.ASK_PHOTOS, reply_markup=k.collect_kb())
        return
    text = t.RESUMED.format(
        photos=daily_text.fa(draft["photos"]),
        rows=daily_text.fa(len(draft["rows"])))
    await cb.message.answer(text, reply_markup=k.collect_kb())


async def entry(cb: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    """Start the flow; if today's draft exists, ask resume or restart."""
    draft = daily_draft.find_today(settings, cb.from_user.id)
    if draft is None:
        await _open(cb, state, settings)
        return
    await state.clear()
    text = t.RESUME_ASK.format(
        photos=daily_text.fa(draft["photos"]),
        rows=daily_text.fa(len(draft["rows"])))
    await cb.message.answer(text, reply_markup=k.resume_kb())


@router.callback_query(F.data == "dp:resume")
async def on_resume(cb: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    if active_admin(settings, cb.from_user.id) is None:
        await cb.answer()
        return
    draft = daily_draft.find_today(settings, cb.from_user.id)
    await _open(cb, state, settings, draft)
    await cb.answer()


@router.callback_query(F.data == "dp:fresh")
async def on_fresh(cb: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    if active_admin(settings, cb.from_user.id) is None:
        await cb.answer()
        return
    old = daily_draft.find_today(settings, cb.from_user.id)
    if old is not None:
        daily_draft.close(settings, old["id"], "cancelled")
    await _open(cb, state, settings)
    await cb.answer()
