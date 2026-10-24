"""تست منطق ورود ادمین (زمان تزریق می‌شود)."""
from datetime import datetime, timedelta

from app.core import admin_auth as auth
from app.core.passwords import hash_password
from app.data import repo_admins

NOW = datetime(2026, 1, 1, 12, 0, 0)
PW = "Abcdef1234"


def make_admin(conn, **fields):
    repo_admins.ensure_owner(conn, 7)
    repo_admins.set_password(conn, 7, hash_password(PW))
    if fields:
        sets = ", ".join(f"{k}=?" for k in fields)
        conn.execute(f"UPDATE admins SET {sets} WHERE tg_id=7", tuple(fields.values()))
        conn.commit()
    return repo_admins.get_admin(conn, 7)


def test_unknown_or_inactive_is_silent(conn):
    assert auth.try_login(None, PW, NOW).status == "silent"
    admin = make_admin(conn, is_active=0)
    assert auth.try_login(admin, PW, NOW).status == "silent"


def test_correct_password_opens_30_min_session(conn):
    result = auth.try_login(make_admin(conn), PW, NOW)
    assert result.status == "ok"
    end = datetime.strptime(result.session_until, auth.FMT)
    assert end - NOW == timedelta(minutes=30)


def test_wrong_password_counts(conn):
    result = auth.try_login(make_admin(conn, failed_count=2), "bad", NOW)
    assert (result.status, result.failed_count) == ("wrong", 3)


def test_fifth_wrong_locks_15_minutes(conn):
    result = auth.try_login(make_admin(conn, failed_count=4), "bad", NOW)
    assert result.status == "now_locked"
    end = datetime.strptime(result.locked_until, auth.FMT)
    assert end - NOW == timedelta(minutes=15)


def test_locked_rejects_even_correct_password(conn):
    until = (NOW + timedelta(minutes=5)).strftime(auth.FMT)
    admin = make_admin(conn, locked_until=until)
    assert auth.try_login(admin, PW, NOW).status == "locked"


def test_lock_expires(conn):
    until = (NOW - timedelta(minutes=1)).strftime(auth.FMT)
    admin = make_admin(conn, locked_until=until)
    assert auth.try_login(admin, PW, NOW).status == "ok"


def test_session_expiry(conn):
    until = (NOW + timedelta(minutes=1)).strftime(auth.FMT)
    admin = make_admin(conn, session_until=until)
    assert auth.has_session(admin, NOW) is True
    assert auth.has_session(admin, NOW + timedelta(minutes=2)) is False


def test_owner_without_password_needs_setup(conn):
    repo_admins.ensure_owner(conn, 7)
    admin = repo_admins.get_admin(conn, 7)
    assert auth.try_login(admin, "x", NOW).status == "need_password"
