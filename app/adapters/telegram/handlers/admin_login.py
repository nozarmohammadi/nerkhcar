"""ورود ادمین: /admin، رمز، حذف پیام رمز."""
import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.adapters.telegram.keyboards.admin_panel import panel_kb
from app.adapters.telegram.texts import admin as t
from app.adapters.telegram.texts import admin_panel as p
from app.config import Settings
from app.core import admin_auth as auth
from app.core.password_policy import check_policy
from app.core.passwords import hash_password
from app.data import db, repo_admins, repo_audit

log = logging.getLogger("nerkhcar.admin")
router = Router()
router.message.filter(F.chat.type == "private")


NOT_START = ~F.text.startswith("/start")  # let /start reset the state


class Login(StatesGroup):
    password = State()
    new_password = State()


async def _wipe(message: Message) -> None:
    try:
        await message.delete()
    except Exception:
        log.warning("حذف پیام رمز ممکن نشد")


def _save(conn, uid: int, result: auth.LoginResult) -> None:
    s = result.status
    if s == "ok":
        repo_admins.save_auth_state(conn, uid, 0, None, result.session_until)
        repo_audit.add_entry(conn, uid, "login_ok")
    elif s == "wrong":
        repo_admins.save_auth_state(conn, uid, result.failed_count, None, None)
        repo_audit.add_entry(conn, uid, "login_fail")
    elif s == "now_locked":
        repo_admins.save_auth_state(conn, uid, 0, result.locked_until, None)
        repo_audit.add_entry(conn, uid, "locked")


async def _reply(message: Message, result: auth.LoginResult) -> None:
    texts = {"ok": t.LOGIN_OK, "wrong": t.WRONG,
             "locked": t.LOCKED, "now_locked": t.NOW_LOCKED}
    text = texts.get(result.status)
    if text:
        await message.answer(text.format(left=auth.MAX_FAILS - result.failed_count))


@router.message(Command("admin"))
async def on_admin(message: Message, state: FSMContext, settings: Settings) -> None:
    conn = db.connect(settings.db_path)
    try:
        admin = repo_admins.get_admin(conn, message.from_user.id)
    finally:
        conn.close()
    if admin is None or not admin.is_active:
        return
    if auth.has_session(admin, datetime.now()):
        await message.answer(p.PANEL_TITLE, reply_markup=panel_kb(admin.role))
    elif admin.pw_hash is None or admin.must_change:
        await state.set_state(Login.new_password)
        await message.answer(t.ASK_NEW_PASSWORD)
    else:
        await state.set_state(Login.password)
        await message.answer(t.ASK_PW_PROMPT)


@router.message(Login.password, F.text, NOT_START)
async def on_password(message: Message, state: FSMContext, settings: Settings) -> None:
    await _wipe(message)
    uid = message.from_user.id
    conn = db.connect(settings.db_path)
    try:
        admin = repo_admins.get_admin(conn, uid)
        result = auth.try_login(admin, message.text, datetime.now())
        _save(conn, uid, result)
    finally:
        conn.close()
    if result.status != "wrong":
        await state.clear()
    await _reply(message, result)
    if result.status == "ok":
        await message.answer(p.PANEL_TITLE, reply_markup=panel_kb(admin.role))
    if result.status == "now_locked":
        alert = t.OWNER_ALERT.format(uid=uid)
        await message.bot.send_message(settings.owner_id, alert)


@router.message(Login.new_password, F.text, NOT_START)
async def on_new_password(
    message: Message, state: FSMContext, settings: Settings
) -> None:
    await _wipe(message)
    problem = check_policy(message.text)
    if problem:
        await message.answer(t.POLICY[problem])
        return
    uid = message.from_user.id
    conn = db.connect(settings.db_path)
    try:
        admin = repo_admins.get_admin(conn, uid)
        if admin and admin.is_active and (admin.pw_hash is None or admin.must_change):
            repo_admins.set_password(conn, uid, hash_password(message.text))
            repo_audit.add_entry(conn, uid, "password_set")
            await message.answer(t.PASSWORD_SET)
    finally:
        conn.close()
    await state.clear()
