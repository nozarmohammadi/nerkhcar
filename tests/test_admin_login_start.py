"""Tests: /start must not be taken as an admin password."""
from types import SimpleNamespace

from app.adapters.telegram.handlers import admin_login


def _msg(text):
    return SimpleNamespace(text=text)


def test_start_is_not_a_password():
    assert not admin_login.NOT_START.resolve(_msg("/start"))
    assert not admin_login.NOT_START.resolve(_msg("/start@nerkhcar_bot"))


def test_normal_text_is_still_a_password():
    assert admin_login.NOT_START.resolve(_msg("Abc123!x"))
