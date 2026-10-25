"""Build the daily price video with ffmpeg: frames, music, then mux."""
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable

log = logging.getLogger("nerkhcar.video")
BASE = ["nice", "-n", "19", "ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
TIMEOUT = 180
FPS = 15
NOTES = (261.63, 329.63, 392.0)  # synthetic C major chord, no copyright
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


def _audio_args(folder: Path, total: float) -> list[str]:
    args: list[str] = []
    for freq in NOTES:
        args += ["-f", "lavfi", "-i", f"sine=frequency={freq}:duration={total:.2f}"]
    fade_out_at = max(total - FADE_OUT, 0)
    graph = (
        "[0:a][1:a][2:a]amix=inputs=3,volume=2,tremolo=f=0.5:d=0.3,"
        f"afade=t=in:d={FADE_IN},afade=t=out:st={fade_out_at:.2f}:d={FADE_OUT}[a]"
    )
    return args + [
        "-filter_complex", graph, "-map", "[a]",
        "-c:a", "aac", "-b:a", "96k", str(folder / "a.m4a"),
    ]


def make_video(frames: Iterable[tuple[bytes, float]]) -> bytes:
    """Return MP4 bytes for the frames with synthetic background music."""
    with tempfile.TemporaryDirectory(prefix="nerkh_vid_") as tmp:
        folder = Path(tmp)
        total = _write_frames(frames, folder)
        _run(_video_args(folder))
        _run(_audio_args(folder, total))
        _run([
            "-i", str(folder / "v.mp4"), "-i", str(folder / "a.m4a"),
            "-map", "0:v", "-map", "1:a", "-c", "copy", "-shortest",
            "-movflags", "+faststart", str(folder / "out.mp4"),
        ])
        return (folder / "out.mp4").read_bytes()
