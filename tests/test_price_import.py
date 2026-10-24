"""تست ثبت قیمت از عکس (بخش ۱)."""
from app.config import Settings
from types import SimpleNamespace
import asyncio
from app.data import db
from app.adapters.telegram.handlers import price_import as h
from app.adapters.telegram.texts import price_import as t
from pi_helpers import FakeBot
from pi_helpers import FakeCb
from pi_helpers import FakeFile
from pi_helpers import FakeMsg
from pi_helpers import FakeState
from pi_helpers import _patch_ai
from pi_helpers import _to_review
from pi_helpers import env


def test_start_guards(env):
    settings, brand = env
    state = FakeState()

    async def run():
        await h.on_start(FakeCb(7, f"pi:{brand}"), state, settings)
        assert state.name is h.PriceImport.source
        assert state.data == {"brand_id": brand}
        other = FakeState()
        nobrand = FakeCb(7, "pi:999")
        await h.on_start(nobrand, other, settings)
        assert nobrand.alerts == [t.NO_BRAND] and other.name is None
        stranger = FakeCb(999, f"pi:{brand}")
        await h.on_start(stranger, other, settings)
        assert stranger.alerts == [None] and other.name is None
        nokey = Settings("tok", 7, settings.db_path, settings.log_dir)
        nk = FakeCb(7, f"pi:{brand}")
        await h.on_start(nk, other, nokey)
        assert nk.alerts == [t.NO_KEY] and other.name is None

    asyncio.run(run())


def test_source_validation(env):
    settings, brand = env
    state = FakeState()

    async def run():
        await h.on_start(FakeCb(7, f"pi:{brand}"), state, settings)
        bad = FakeMsg(7, "/start")
        await h.on_source(bad, state, settings)
        assert bad.answers == [t.BAD_SOURCE]
        assert state.name is h.PriceImport.source
        await h.on_source(FakeMsg(7, "  auto_price "), state, settings)
        assert state.name is h.PriceImport.photo
        assert state.data["source"] == "auto_price"

    asyncio.run(run())


def test_full_flow_edit_and_save(env, monkeypatch):
    settings, brand = env
    _patch_ai(monkeypatch)
    state = FakeState()

    async def run():
        msg = await _to_review(settings, brand, state)
        assert state.name is h.PriceImport.review
        assert msg.answers[0] == t.READING and msg.answers[-1] == t.HELP
        assert "ساینا اتومات" in msg.answers[1]
        assert t.FLAG_LABELS["no_price"] in msg.answers[1]
        edit = FakeMsg(7, "3 قیمت 1900")
        await h.on_edit(edit, state, settings)
        assert state.data["rows"][2]["price_m"] == 1900
        assert t.FLAG_LABELS["no_price"] not in edit.answers[0]
        cb = FakeCb(7, "pi:ok")
        await h.on_confirm(cb, state, settings)
        assert t.SAVED.format(saved=3, blocked=0) in cb.message.answers[0]
        assert state.name is h.PriceImport.photo

    asyncio.run(run())
    conn = db.connect(settings.db_path)
    rows = conn.execute(
        "SELECT source_name, low FROM reference_prices ORDER BY id").fetchall()
    conn.close()
    assert [tuple(r) for r in rows] == [
        ("auto_price", 1720), ("auto_price", 1810), ("auto_price", 1900)]


def test_photo_state_inputs(env, monkeypatch):
    settings, brand = env
    _patch_ai(monkeypatch)
    state = FakeState()

    async def run():
        await h.on_start(FakeCb(7, f"pi:{brand}"), state, settings)
        await h.on_source(FakeMsg(7, "auto_price"), state, settings)
        big = FakeMsg(7, photo=[FakeFile(size=h.MAX_BYTES + 1)])
        await h.on_photo(big, state, settings, FakeBot())
        assert big.answers == [t.TOO_BIG]
        assert state.name is h.PriceImport.photo
        wrong = FakeMsg(7, "hello")
        await h.on_need_photo(wrong)
        assert wrong.answers == [t.NEED_PHOTO]
        doc = SimpleNamespace(file_size=100, mime_type="image/png")
        await h.on_photo(FakeMsg(7, document=doc), state, settings, FakeBot())
        assert state.name is h.PriceImport.review

    asyncio.run(run())


def test_read_error_keeps_waiting(env, monkeypatch):
    settings, brand = env
    _patch_ai(monkeypatch, status="rate_limit", text="")
    state = FakeState()

    async def run():
        msg = await _to_review(settings, brand, state)
        assert msg.answers == [t.READING, t.READ_ERRORS["rate_limit"]]
        assert state.name is h.PriceImport.photo

    asyncio.run(run())


def test_bad_edit_commands(env, monkeypatch):
    settings, brand = env
    _patch_ai(monkeypatch)
    state = FakeState()
    cases = (
        ("abc", t.BAD_COMMAND),
        ("9 قیمت 5", t.EDIT_ERRORS["bad_index"]),
        ("1 قیمت x", t.EDIT_ERRORS["bad_value"]),
    )

    async def run():
        await _to_review(settings, brand, state)
        for text, expected in cases:
            msg = FakeMsg(7, text)
            await h.on_edit(msg, state, settings)
            assert msg.answers == [expected]

    asyncio.run(run())


_FIXTURES = (env,)
