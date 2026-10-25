"""ffmpeg video builder: real run on tiny frames, and temp cleanup."""
import shutil
import tempfile
from glob import glob
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from app.adapters import music_store, video_ffmpeg

pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None, reason="ffmpeg not installed")


@pytest.fixture(autouse=True)
def no_music(tmp_path, monkeypatch):
    """Keep these tests silent and independent of the real music file."""
    monkeypatch.setattr(music_store, "MUSIC_PATH", tmp_path / "none.mp3")


def _png(color: tuple) -> bytes:
    out = BytesIO()
    Image.new("RGB", (64, 64), color).save(out, "PNG")
    return out.getvalue()


def _leftovers() -> list[str]:
    return glob(str(Path(tempfile.gettempdir()) / "nerkh_vid_*"))


def test_make_video_returns_mp4_and_cleans_up():
    frames = [(_png((i * 40, 0, 0)), 0.4) for i in range(3)]
    data = video_ffmpeg.make_video(frames)
    assert data[4:8] == b"ftyp"
    assert len(data) > 500
    assert _leftovers() == []


def test_no_frames_raises_and_cleans_up():
    with pytest.raises(video_ffmpeg.VideoError):
        video_ffmpeg.make_video([])
    assert _leftovers() == []
