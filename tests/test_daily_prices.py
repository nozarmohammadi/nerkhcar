"""تست قیمت روز خودرو (پیام‌های ساختگی؛ بدون شبکه)."""

from app.adapters.telegram.handlers import daily_prices as h
from app.adapters.telegram.keyboards import admin_panel as k_panel
from app.adapters.telegram.texts import daily_prices as t
from app.core import daily_text, table_parse

RAW = [
    {"name": "سهند", "year": 1405, "price": 1810000000, "change": 5000000},
    {"name": "ساینا اس", "year": 1405, "price": 1720000000, "change": -15000000},
    {"name": "ساینا اتومات", "year": 1405, "price": None, "change": None},
]


def test_merge_drops_blocked_and_replaces_duplicates():
    rows = table_parse.normalize_rows(RAW)
    total = daily_text.merge_rows([], rows)
    assert [r["name"] for r in total] == ["سهند", "ساینا اس"]
    newer = table_parse.normalize_rows([dict(RAW[0], price=1900000000)])
    total = daily_text.merge_rows(total, newer)
    assert len(total) == 2 and total[0]["price_m"] == 1900


def test_build_text_has_prices_and_arrows():
    rows = daily_text.merge_rows([], table_parse.normalize_rows(RAW))
    text = daily_text.build_text(rows, "2026-10-24", t)
    assert "1,810" in text and "🟢" in text and "🔴" in text
    assert "ساینا اتومات" not in text and "2026-10-24" in text


def test_panel_has_daily_button():
    for role in ("owner", "editor"):
        kb = k_panel.panel_kb(role)
        assert "dp:go" in [row[0].callback_data for row in kb.inline_keyboard]


def test_router_registered():
    from app import main
    assert h.router in [m.router for m in main.ROUTER_MODULES]
