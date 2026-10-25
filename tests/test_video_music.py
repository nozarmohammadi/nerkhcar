"""Video music: real audio is looped and trimmed; no file means silent."""
import json
import logging
import shutil
import subprocess
from io import BytesIO

import pytest
from PIL import Image

from app.adapters import music_store, video_ffmpeg

pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="ffmpeg not installed")


def _frames(count: int) -> list[tuple[bytes, float]]:
    out = BytesIO()
    Image.new("RGB", (64, 64), (90, 0, 0)).save(out, "PNG")
    return [(out.getvalue(), 1.0) for _ in range(count)]


def _wav(tmp_path, seconds: int):
    path = tmp_path / f"m{seconds}.wav"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
        "-i", f"sine=frequency=330:duration={seconds}", str(path),
    ], check=True, timeout=30)
    return path


def _info(data: bytes, tmp_path) -> tuple[bool, float]:
    out = tmp_path / "o.mp4"
    out.write_bytes(data)
    run = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_type", "-of", "json", str(out),
    ], capture_output=True, text=True, check=True)
    info = json.loads(run.stdout)
    has_audio = any(s["codec_type"] == "audio" for s in info["streams"])
    return has_audio, float(info["format"]["duration"])


def test_short_music_is_looped(tmp_path):
    data = video_ffmpeg.make_video(_frames(4), music=_wav(tmp_path, 2))
    has_audio, seconds = _info(data, tmp_path)
    assert has_audio
    assert 3.4 < seconds < 4.8


def test_long_music_is_trimmed(tmp_path):
    data = video_ffmpeg.make_video(_frames(2), music=_wav(tmp_path, 12))
    has_audio, seconds = _info(data, tmp_path)
    assert has_audio
    assert seconds < 3.5


def test_default_path_is_used(tmp_path, monkeypatch):
    monkeypatch.setattr(music_store, "MUSIC_PATH", _wav(tmp_path, 5))
    has_audio, _ = _info(video_ffmpeg.make_video(_frames(2)), tmp_path)
    assert has_audio


def test_missing_music_is_silent_with_warning(tmp_path, monkeypatch, caplog):
    monkeypatch.setattr(music_store, "MUSIC_PATH", tmp_path / "none.mp3")
    with caplog.at_level(logging.WARNING, logger="nerkhcar.video"):
        data = video_ffmpeg.make_video(_frames(2))
    assert _info(data, tmp_path)[0] is False
    assert "silent" in caplog.text


def test_bad_music_file_falls_back_to_silent(tmp_path):
    bad = tmp_path / "bad.mp3"
    bad.write_bytes(b"not audio at all")
    data = video_ffmpeg.make_video(_frames(2), music=bad)
    assert _info(data, tmp_path)[0] is False
