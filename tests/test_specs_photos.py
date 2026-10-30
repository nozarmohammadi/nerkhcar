import asyncio
import io

from aiogram.exceptions import TelegramAPIError
from PIL import Image

from app.adapters.telegram import specs_send
from app.adapters.telegram.texts import specs as t
from app.core import car_images as ci
from app.core import specs_html


def _jpeg() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), (0, 128, 0)).save(buf, "JPEG")
    return buf.getvalue()


def test_slideshow_in_html():
    html = specs_html.build_html("t", [("a", "1")], ("x", "y"), "b1", ("ph1", "ph2"))
    assert html.count("<tg-slideshow>") == 1
    assert "tg://photo?id=ph2" in html


def test_no_slideshow_without_photos():
    html = specs_html.build_html("t", [("a", "1")], ("x", "y"), "b1")
    assert "tg-slideshow" not in html


def test_load_reads_files_and_rejects_bad_slug(tmp_path):
    folder = tmp_path / "car-1"
    folder.mkdir()
    (folder / "1.jpg").write_bytes(b"a")
    (folder / "2.jpg").write_bytes(b"b")
    assert ci.load("car-1", tmp_path) == [b"a", b"b"]
    assert ci.load("missing", tmp_path) == []
    assert ci.load("../etc", tmp_path) == []


def test_rich_media_count():
    rich = specs_send._rich("t", [("a", "1")], "car", t.THEMES[0], [_jpeg(), _jpeg()])
    assert len(rich.media) == 3


class FakeBot:
    def __init__(self):
        self.calls = []

    async def send_rich_message(self, chat_id, rich_message):
        self.calls.append(len(rich_message.media))
        if len(rich_message.media) > 1:
            raise TelegramAPIError(method=None, message="bad")

    async def send_message(self, chat_id, text):
        self.calls.append("text")


def test_falls_back_to_cover_without_photos(tmp_path, monkeypatch):
    (tmp_path / "s1").mkdir()
    (tmp_path / "s1" / "1.jpg").write_bytes(_jpeg())
    monkeypatch.setattr(ci, "ROOT", tmp_path)
    bot = FakeBot()
    result = asyncio.run(specs_send.send_table(
        bot, 1, "t", [("a", "1")], "car", t.THEMES[0], slug="s1"))
    assert result == "rich"
    assert bot.calls == [2, 1]
