"""مدیریت ادمین‌ها (فقط مالک). منطق خالص، بدون تلگرام."""
import secrets
import sqlite3
import string

from app.core.passwords import hash_password
from app.data import repo_admins, repo_audit

ROLES = ("owner", "editor")
_ALPHABET = string.ascii_letters + string.digits


def new_temp_password(length: int = 14) -> str:
    """رمز موقتی تصادفی؛ همیشه شامل حرف و عدد است."""
    while True:
        pw = "".join(secrets.choice(_ALPHABET) for _ in range(length))
        if any(c.isalpha() for c in pw) and any(c.isdigit() for c in pw):
            return pw


def can_manage(actor) -> bool:
    return actor is not None and actor.is_active and actor.role == "owner"


def add_editor(conn: sqlite3.Connection, actor, new_id: int) -> tuple[str, str | None]:
    """نتیجه: (کد، رمز موقتی). رمز فقط همین یک بار برمی‌گردد."""
    if not can_manage(actor):
        return "forbidden", None
    if repo_admins.get_admin(conn, new_id):
        return "exists", None
    temp = new_temp_password()
    repo_admins.add_admin(conn, new_id, "editor", hash_password(temp))
    repo_audit.add_entry(conn, actor.tg_id, "admin_added", f"id={new_id} role=editor")
    return "ok", temp


def remove_admin(conn: sqlite3.Connection, actor, target_id: int) -> str:
    if not can_manage(actor):
        return "forbidden"
    target = repo_admins.get_admin(conn, target_id)
    if target is None:
        return "not_found"
    if target.role == "owner":
        return "cannot_remove_owner"
    repo_admins.set_active(conn, target_id, False)
    repo_audit.add_entry(conn, actor.tg_id, "admin_removed", f"id={target_id}")
    return "ok"


def reset_password(conn: sqlite3.Connection, actor, target_id: int) -> tuple[str, str | None]:
    if not can_manage(actor):
        return "forbidden", None
    target = repo_admins.get_admin(conn, target_id)
    if target is None or target.role == "owner":
        return "not_found", None
    temp = new_temp_password()
    repo_admins.set_temp_password(conn, target_id, hash_password(temp))
    repo_audit.add_entry(conn, actor.tg_id, "password_reset", f"id={target_id}")
    return "ok", temp


def can_edit_prices(admin) -> bool:
    return admin is not None and admin.is_active and admin.role in ROLES
