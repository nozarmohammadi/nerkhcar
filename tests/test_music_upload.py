"""Music upload storage: validation, replace and backup."""
import subprocess

import pytest

from app.adapters import music_store


def _wav(tmp_path, seconds: int) -> bytes:
    out = tmp_path / "t.wav"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
        "-i", f"sine=frequency=440:duration={seconds}", str(out),
    ], check=True, timeout=30)
    return out.read_bytes()


@pytest.fixture
def target(tmp_path, monkeypatch):
    path = tmp_path / "music" / "bed.mp3"
    monkeypatch.setattr(music_store, "MUSIC_PATH", path)
    return path


def test_save_valid_audio(tmp_path, target):
    seconds = music_store.save_music(_wav(tmp_path, 12))
    assert 11 < seconds < 13
    assert target.exists()
    assert not target.with_suffix(".tmp").exists()


def test_replace_keeps_previous(tmp_path, target):
    music_store.save_music(_wav(tmp_path, 12))
    music_store.save_music(_wav(tmp_path, 14))
    assert target.with_suffix(".prev").exists()


def test_garbage_is_rejected(target):
    with pytest.raises(music_store.MusicError):
        music_store.save_music(b"this is not audio")
    assert not target.exists()
    assert not target.with_suffix(".tmp").exists()


def test_too_short_is_rejected(tmp_path, target):
    with pytest.raises(music_store.MusicError):
        music_store.save_music(_wav(tmp_path, 3))
    assert not target.exists()
