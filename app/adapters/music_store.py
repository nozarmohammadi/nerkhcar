"""Store the video background music file: validate, back up, replace."""
import json
import logging
import os
import shutil
import subprocess
from pathlib import Path

log = logging.getLogger("nerkhcar.music")
MUSIC_PATH = Path(__file__).resolve().parents[2] / "assets" / "music" / "bed.mp3"
MIN_SEC = 10
MAX_SEC = 600
PROBE_TIMEOUT = 20


class MusicError(ValueError):
    """Raised when the uploaded file is not usable music."""


def probe_seconds(path: Path) -> float:
    """Return the audio duration in seconds, or raise MusicError."""
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "format=duration:stream=codec_type",
        "-of", "json", str(path),
    ]
    try:
        run = subprocess.run(
            cmd, check=True, timeout=PROBE_TIMEOUT,
            capture_output=True, text=True)
        data = json.loads(run.stdout)
        seconds = float(data["format"]["duration"])
        has_audio = bool(data.get("streams"))
    except (subprocess.SubprocessError, OSError, ValueError, KeyError) as exc:
        log.warning("music probe failed: %s", type(exc).__name__)
        raise MusicError(type(exc).__name__) from exc
    if not has_audio or not MIN_SEC <= seconds <= MAX_SEC:
        raise MusicError("no audio or bad length")
    return seconds


def save_music(data: bytes) -> float:
    """Validate the bytes, keep the old file as .prev, then replace it."""
    MUSIC_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = MUSIC_PATH.with_suffix(".tmp")
    tmp.write_bytes(data)
    try:
        seconds = probe_seconds(tmp)
        if MUSIC_PATH.exists():
            shutil.copy2(MUSIC_PATH, MUSIC_PATH.with_suffix(".prev"))
        os.replace(tmp, MUSIC_PATH)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    return seconds
