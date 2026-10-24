"""تست امنیتی ورود و نشست ادمین."""
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from app.adapters.telegram.guard import active_admin, owner_only
from app.config import Settings
from app.core import admin_auth as auth
from app.core import admin_manage as manage
from app.core.passwords import hash_password
from app.data import db, repo_admins

NOW = datetime(2026, 1, 1, 12, 0, 0)
GOOD_PW = "Abcdef1234xyz"
HASH = hash_password(GOOD_PW)


def _fake(fails=0, must=0, session=None):
    return SimpleNamespace(
        is_active=1, locked_until=None, pw_hash=HASH, must_change=must,
        failed_count=fails, session_until=session,
    )


def _live(minutes=30):
    return (datetime.now() + timedelta(minutes=minutes)).strftime(auth.FMT)


@pytest.fixture
def settings(tmp_path):
    path = tmp_path / "t.db"
    (tmp_path / "b").mkdir()
    db.migrate(path, tmp_path / "b")
    conn = db.connect(path)
    repo_admins.ensure_owner(conn, 7)
    repo_admins.save_auth_state(conn, 7, 0, None, _live())
    repo_admins.add_admin(conn, 55, "editor")
    repo_admins.save_auth_state(conn, 55, 0, None, _live())
    conn.close()
    return Settings("tok", 7, path, tmp_path)


def test_removed_admin_with_live_session_is_silent(settings):
    conn = db.connect(settings.db_path)
    owner = repo_admins.get_admin(conn, 7)
    assert manage.remove_admin(conn, owner, 55) == "ok"
    conn.close()
    assert active_admin(settings, 55) is None
    assert auth.try_login(repo_admins.get_admin(
        db.connect(settings.db_path), 55), "x", NOW).status == "silent"


def test_expired_session_blocks_guard(settings):
    conn = db.connect(settings.db_path)
    repo_admins.save_auth_state(conn, 7, 0, None, _live(-1))
    conn.close()
    assert active_admin(settings, 7) is None
    assert owner_only(settings, 7) is None


def test_session_ends_exactly_at_deadline():
    end = NOW.strftime(auth.FMT)
    assert auth.has_session(_fake(session=end), NOW) is False
    before = NOW - timedelta(seconds=1)
    assert auth.has_session(_fake(session=end), before) is True


def test_fourth_wrong_no_lock_fifth_locks():
    admin = _fake()
    for i in range(4):
        res = auth.try_login(admin, "bad", NOW)
        assert res.status == "wrong" and res.failed_count == i + 1
        admin.failed_count = res.failed_count
    res = auth.try_login(admin, "bad", NOW)
    assert res.status == "now_locked"
    assert res.locked_until == (NOW + timedelta(minutes=15)).strftime(auth.FMT)


def test_success_resets_fail_counter():
    res = auth.try_login(_fake(fails=4), GOOD_PW, NOW)
    assert res.status == "ok" and res.failed_count == 0
    assert res.session_until == (NOW + timedelta(minutes=30)).strftime(auth.FMT)


def test_hash_hides_secret_and_rejects_wrong():
    assert GOOD_PW not in HASH and HASH != GOOD_PW
    assert auth.try_login(_fake(), "wrong-one", NOW).status == "wrong"


def test_must_change_blocks_even_correct_pw():
    res = auth.try_login(_fake(must=1), GOOD_PW, NOW)
    assert res.status == "need_password" and res.session_until is None


def test_editor_with_live_session_is_not_owner(settings):
    assert active_admin(settings, 55) is not None
    assert owner_only(settings, 55) is None


def test_unknown_id_gets_nothing_from_guard(settings):
    assert active_admin(settings, 999) is None
    assert owner_only(settings, 999) is None
