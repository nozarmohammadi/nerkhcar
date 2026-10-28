"""Test: admin handlers use the shared deny helper (expired session message)."""
from app.adapters.telegram.handlers import admin_audit, admin_manage, price_import


def test_panel_handlers_use_deny():
    for module in (admin_audit, admin_manage, price_import):
        assert hasattr(module, "deny")
