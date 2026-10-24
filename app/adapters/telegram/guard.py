"""نگهبان پنل: نشست فعال و نقش مالک را چک می‌کند."""
from datetime import datetime

from app.config import Settings
from app.core import admin_auth, admin_manage
from app.data import db, repo_admins
from app.data.models import Admin


def active_admin(settings: Settings, uid: int) -> Admin | None:
    conn = db.connect(settings.db_path)
    try:
        admin = repo_admins.get_admin(conn, uid)
    finally:
        conn.close()
    if admin and admin.is_active and admin_auth.has_session(admin, datetime.now()):
        return admin
    return None


def owner_only(settings: Settings, uid: int) -> Admin | None:
    admin = active_admin(settings, uid)
    return admin if admin_manage.can_manage(admin) else None
