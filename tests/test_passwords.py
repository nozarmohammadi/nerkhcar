"""تست هش و قانون رمز و ثبت مالک."""
from app.core.password_policy import check_policy
from app.core.passwords import hash_password, verify_password
from app.data import repo_admins


def test_hash_and_verify():
    h = hash_password("Abcdef1234")
    assert h != "Abcdef1234"
    assert verify_password(h, "Abcdef1234")
    assert not verify_password(h, "wrong-pass-1")
    assert not verify_password("not-a-hash", "x")


def test_policy():
    assert check_policy("short1") == "too_short"
    assert check_policy("1234567890") == "no_letter"
    assert check_policy("abcdefghij") == "no_digit"
    assert check_policy("Abcdef1234") is None


def test_owner_created_once_without_password(conn):
    assert repo_admins.ensure_owner(conn, 7) is True
    assert repo_admins.ensure_owner(conn, 7) is False
    admin = repo_admins.get_admin(conn, 7)
    assert admin.role == "owner" and admin.pw_hash is None and admin.must_change == 1


def test_set_password_stores_hash_only(conn):
    repo_admins.ensure_owner(conn, 7)
    repo_admins.set_password(conn, 7, hash_password("Abcdef1234"))
    admin = repo_admins.get_admin(conn, 7)
    assert admin.pw_hash.startswith("$argon2")
    assert "Abcdef1234" not in admin.pw_hash
    assert admin.must_change == 0
