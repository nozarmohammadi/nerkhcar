"""Daily video button: admin check, empty data, busy lock, success, failure."""
import asyncio
from types import SimpleNamespace

from app.adapters.telegram.handlers import daily_video as h
from app.adapters.telegram.texts import daily_prices as t


class Note:
    def __init__(self, log):
        self.log = log

    async def edit_text(self, text):
        self.log.append(("edit", text))

    async def delete(self):
        self.log.append(("delete",))


class Msg:
    def __init__(self, log):
        self.log = log

    async def answer(self, text):
        self.log.append(("answer", text))
        return Note(self.log)

    async def answer_video(self, video, **kw):
        self.log.append(("video", kw))


class Cb:
    def __init__(self, log):
        self.log = log
        self.message = Msg(log)
        self.from_user = SimpleNamespace(id=1)

    async def answer(self, text=None, show_alert=False):
        self.log.append(("cb", text, show_alert))


class State:
    def __init__(self, data):
        self.data = data
        self.cleared = False

    async def get_data(self):
        return self.data

    async def clear(self):
        self.cleared = True


def _run(monkeypatch, admin, data, build=None, hold=False):
    log, state = [], State(data)
    monkeypatch.setattr(h, "active_admin", lambda s, uid: admin)
    if build:
        monkeypatch.setattr(h, "_build", build)

    async def go():
        if hold:
            async with h._LOCK:
                await h.on_video(Cb(log), state, object())
        else:
            await h.on_video(Cb(log), state, object())

    asyncio.run(go())
    return log, state


def test_non_admin_clears_state_and_sends_nothing(monkeypatch):
    log, state = _run(monkeypatch, None, {"rows": [1]})
    assert state.cleared
    assert log == [("cb", None, False)]


def test_empty_rows_alert(monkeypatch):
    log, _ = _run(monkeypatch, object(), {})
    assert log == [("cb", t.VID_EMPTY, True)]


def test_busy_alert(monkeypatch):
    log, _ = _run(monkeypatch, object(), {"rows": [1]}, hold=True)
    assert log == [("cb", t.VID_BUSY, True)]


def test_success_sends_video_and_removes_status(monkeypatch):
    log, _ = _run(monkeypatch, object(), {"rows": [1]},
                  build=lambda rows: b"video")
    kinds = [entry[0] for entry in log]
    assert kinds == ["cb", "answer", "video", "delete"]
    assert log[2][1]["width"] == 720


def test_failure_shows_error(monkeypatch):
    def boom(rows):
        raise RuntimeError("x")

    log, _ = _run(monkeypatch, object(), {"rows": [1]}, build=boom)
    assert ("edit", t.VID_FAIL) in log
    assert all(entry[0] != "video" for entry in log)
