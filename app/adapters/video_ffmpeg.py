"""Build the daily price video with ffmpeg: frames, music, then mux."""
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable

from app.adapters import music_store

log = logging.getLogger("nerkhcar.video")
BASE = ["nice", "-n", "19", "ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
TIMEOUT = 180
FPS = 15
FADE_IN = 1
FADE_OUT = 2


class VideoError(RuntimeError):
    """Raised when ffmpeg fails, times out or there are no frames."""


def _run(args: list[str]) -> None:
    try:
        subprocess.run(
            BASE + args, check=True, timeout=TIMEOUT, capture_output=True)
    except (subprocess.SubprocessError, OSError) as exc:
        log.warning("ffmpeg step failed: %s", type(exc).__name__)
        raise VideoError(type(exc).__name__) from exc


def _write_frames(frames: Iterable[tuple[bytes, float]], folder: Path) -> float:
    """Save the frames and the concat list; return the total seconds."""
    lines, total, name = [], 0.0, ""
    for i, (png, seconds) in enumerate(frames):
        name = f"f{i:03d}.png"
        (folder / name).write_bytes(png)
        lines += [f"file '{name}'", f"duration {seconds}"]
        total += seconds
    if not name:
        raise VideoError("no frames")
    lines.append(f"file '{name}'")
    (folder / "list.txt").write_text("\n".join(lines) + "\n")
    return total


def _video_args(folder: Path) -> list[str]:
    return [
        "-f", "concat", "-i", str(folder / "list.txt"), "-an",
        "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264",
        "-preset", "ultrafast", "-tune", "stillimage", "-crf", "26",
        "-threads", "1", "-x264-params", "rc-lookahead=0",
        str(folder / "v.mp4"),
    ]


def _mux_args(folder: Path, total: float, track: Path | None) -> list[str]:
    video, out = str(folder / "v.mp4"), str(folder / "out.mp4")
    tail = ["-movflags", "+faststart", out]
    if track is None:
        return ["-i", video, "-c", "copy"] + tail
    fade_out_at = max(total - FADE_OUT, 0)
    fade = (
        f"afade=t=in:d={FADE_IN},"
        f"afade=t=out:st={fade_out_at:.2f}:d={FADE_OUT}"
    )
    return [
        "-i", video, "-stream_loop", "-1", "-i", str(track),
        "-map", "0:v", "-map", "1:a", "-af", fade, "-c:v", "copy",
        "-c:a", "aac", "-b:a", "96k", "-t", f"{total:.2f}", "-shortest",
    ] + tail


def _music_file(music: Path | None) -> Path | None:
    path = music_store.MUSIC_PATH if music is None else music
    if path.is_file():
        return path
    log.warning("music file missing; building a silent video")
    return None


def _mux(folder: Path, total: float, track: Path | None) -> None:
    """Add the looped music; on any music failure build a silent video."""
    try:
        _run(_mux_args(folder, total, track))
    except VideoError:
        if track is None:
            raise
        log.warning("music mux failed; building a silent video")
        _run(_mux_args(folder, total, None))


def make_video(
    frames: Iterable[tuple[bytes, float]], music: Path | None = None
) -> bytes:
    """Return MP4 bytes; the music file (if any) is looped under the video."""
    track = _music_file(music)
    with tempfile.TemporaryDirectory(prefix="nerkh_vid_") as tmp:
        folder = Path(tmp)
        total = _write_frames(frames, folder)
        _run(_video_args(folder))
        _mux(folder, total, track)
        return (folder / "out.mp4").read_bytes()
