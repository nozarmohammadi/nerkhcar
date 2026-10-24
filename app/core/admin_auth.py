"""منطق ورود ادمین: قفل، نشست و شمارش تلاش. بدون تلگرام."""
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.core.passwords import verify_password
from app.data.models import Admin

MAX_FAILS = 5
LOCK_MINUTES = 15
SESSION_MINUTES = 30
FMT = "%Y-%m-%d %H:%M:%S"


@dataclass
class LoginResult:
    status: str  # silent, locked, need_password, ok, wrong, now_locked
    failed_count: int = 0
    locked_until: str | None = None
    session_until: str | None = None


def _parse(value: str | None) -> datetime | None:
    return datetime.strptime(value, FMT) if value else None


def is_locked(admin: Admin, now: datetime) -> bool:
    until = _parse(admin.locked_until)
    return until is not None and until > now


def has_session(admin: Admin, now: datetime) -> bool:
    until = _parse(admin.session_until)
    return until is not None and until > now


def try_login(admin: Admin | None, password: str, now: datetime) -> LoginResult:
    if admin is None or not admin.is_active:
        return LoginResult("silent")
    if is_locked(admin, now):
        return LoginResult("locked", admin.failed_count, admin.locked_until)
    if admin.pw_hash is None or admin.must_change:
        return LoginResult("need_password")
    if verify_password(admin.pw_hash, password):
        end = (now + timedelta(minutes=SESSION_MINUTES)).strftime(FMT)
        return LoginResult("ok", 0, None, end)
    return _fail(admin, now)


def _fail(admin: Admin, now: datetime) -> LoginResult:
    count = admin.failed_count + 1
    if count >= MAX_FAILS:
        end = (now + timedelta(minutes=LOCK_MINUTES)).strftime(FMT)
        return LoginResult("now_locked", 0, end)
    return LoginResult("wrong", count)
