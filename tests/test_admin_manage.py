"""تست مدیریت ادمین‌ها و نقش‌ها."""
from app.core import admin_manage as m
from app.core.passwords import verify_password
from app.data import repo_admins, repo_audit


def owner_and_editor(conn):
    repo_admins.ensure_owner(conn, 1)
    owner = repo_admins.get_admin(conn, 1)
    status, temp = m.add_editor(conn, owner, 2)
    return owner, status, temp


def test_owner_adds_editor_with_temp_password(conn):
    owner, status, temp = owner_and_editor(conn)
    assert status == "ok" and len(temp) == 14
    editor = repo_admins.get_admin(conn, 2)
    assert editor.role == "editor" and editor.must_change == 1
    assert verify_password(editor.pw_hash, temp)
    assert temp not in editor.pw_hash


def test_temp_password_never_in_audit_log(conn):
    _, _, temp = owner_and_editor(conn)
    assert all(temp not in str(e) for e in repo_audit.recent(conn))


def test_editor_cannot_manage(conn):
    owner_and_editor(conn)
    editor = repo_admins.get_admin(conn, 2)
    assert m.add_editor(conn, editor, 3) == ("forbidden", None)
    assert m.remove_admin(conn, editor, 1) == "forbidden"
    assert m.reset_password(conn, editor, 1) == ("forbidden", None)


def test_duplicate_add_rejected(conn):
    owner, _, _ = owner_and_editor(conn)
    assert m.add_editor(conn, owner, 2) == ("exists", None)


def test_owner_cannot_be_removed(conn):
    owner, _, _ = owner_and_editor(conn)
    assert m.remove_admin(conn, owner, 1) == "cannot_remove_owner"


def test_remove_deactivates_and_keeps_audit(conn):
    owner, _, _ = owner_and_editor(conn)
    assert m.remove_admin(conn, owner, 2) == "ok"
    assert repo_admins.get_admin(conn, 2).is_active == 0
    actions = [e["action"] for e in repo_audit.recent(conn)]
    assert "admin_removed" in actions and "admin_added" in actions


def test_reset_password_forces_change(conn):
    owner, _, _ = owner_and_editor(conn)
    status, temp = m.reset_password(conn, owner, 2)
    editor = repo_admins.get_admin(conn, 2)
    assert status == "ok" and editor.must_change == 1
    assert verify_password(editor.pw_hash, temp)


def test_editor_can_edit_prices_only(conn):
    owner, _, _ = owner_and_editor(conn)
    editor = repo_admins.get_admin(conn, 2)
    assert m.can_edit_prices(editor) and m.can_edit_prices(owner)
    assert not m.can_manage(editor)
    m.remove_admin(conn, owner, 2)
    assert not m.can_edit_prices(repo_admins.get_admin(conn, 2))
