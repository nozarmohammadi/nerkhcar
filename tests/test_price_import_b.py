"""تست ثبت قیمت از عکس (بخش ۲)."""
import asyncio
from app.adapters.telegram import draft_view
from app.core import edit_command
from app.adapters.telegram.handlers import price_import as h
from app.adapters.telegram.keyboards import catalog as k_cat
from app import main
from app.adapters.telegram.texts import price_import as t
from app.core import table_parse
from pi_helpers import FakeCb
from pi_helpers import FakeMsg
from pi_helpers import FakeState
from pi_helpers import _patch_ai
from pi_helpers import _to_review
from pi_helpers import env


def test_confirm_with_blocked_rows(env, monkeypatch):
    settings, brand = env
    _patch_ai(monkeypatch)

    async def run():
        first = FakeState()
        await _to_review(settings, brand, first)
        cb = FakeCb(7, "pi:ok")
        await h.on_confirm(cb, first, settings)
        assert t.SAVED.format(saved=2, blocked=1) in cb.message.answers[0]
        second = FakeState()
        await _to_review(settings, brand, second)
        for _ in range(2):
            await h.on_edit(FakeMsg(7, "1 حذف"), second, settings)
        cb2 = FakeCb(7, "pi:ok")
        await h.on_confirm(cb2, second, settings)
        assert cb2.message.answers == [t.NOTHING_READY]
        assert second.name is h.PriceImport.review

    asyncio.run(run())


def test_cancel_clears_state():
    state = FakeState()
    state.name = h.PriceImport.review
    cb = FakeCb(7, "pi:x")
    asyncio.run(h.on_cancel(cb, state))
    assert state.name is None and cb.message.answers == [t.CANCELLED]


def test_draft_view_chunks_and_flags():
    raw = [{"name": f"m{i}", "year": 1405, "price": 1720000000} for i in range(30)]
    raw.append({"name": "x", "year": 2025, "price": None})
    chunks = draft_view.draft_chunks(table_parse.normalize_rows(raw), "auto_price")
    assert len(chunks) == 2
    assert "auto_price" in chunks[0] and "1)" in chunks[0]
    assert t.FLAG_LABELS["no_price"] in chunks[1]
    assert t.FLAG_LABELS["greg_year"] in chunks[1]
    assert t.EMPTY_DRAFT in draft_view.draft_chunks([], "s")[0]


def test_parse_edit_variants():
    kw = t.KEYWORDS
    assert edit_command.parse_edit("3 قیمت 1750", kw) == (3, "price", "1750")
    assert edit_command.parse_edit("۳ حذف", kw) == (3, "delete", "")
    assert edit_command.parse_edit("3 نام ساینا اس", kw) == (3, "name", "ساینا اس")
    assert edit_command.parse_edit("x قیمت 1", kw) is None
    assert edit_command.parse_edit("3 رنگ 1", kw) is None
    assert edit_command.parse_edit("3", kw) is None
    assert edit_command.parse_edit("", kw) is None


def test_dispatcher_includes_import_router(env):
    settings, _ = env
    dp = main.build_dispatcher(settings)
    assert h.router.parent_router is dp


def test_models_keyboard_has_import_button():
    kb = k_cat.models_kb(5, [{"id": 1, "name": "m"}])
    assert "pi:5" in [row[0].callback_data for row in kb.inline_keyboard]


_FIXTURES = (env,)
