"""Pick car photo names from a Zoomit page and convert photos to JPEG."""
import io
import re
from pathlib import Path

from PIL import Image

MEDIA_RE = re.compile(r"api2\.zoomit\.ir(?:\\?/)media(?:\\?/)([A-Za-z0-9._-]+)")
SKIP = ("logo", "untitled")
MAX_PHOTOS = 4
ANGLES = ("front-side", "front", "side", "back-side", "back", "grill", "top")
LAST = len(ANGLES) + 1


def media_names(page: str) -> list[str]:
    """All media names in page order, without duplicates."""
    seen: list[str] = []
    for name in MEDIA_RE.findall(page):
        if name not in seen:
            seen.append(name)
    return seen


def is_car_photo(name: str) -> bool:
    """False for logos and other non-car images."""
    return not any(word in name for word in SKIP)


def rank(name: str) -> int:
    """Sort key: untitled main photo first, interior shots last."""
    if "-inside-" in name or "-seats-" in name:
        return LAST
    for i, angle in enumerate(ANGLES, 1):
        if f"-{angle}-" in name:
            return i
    return 0


def pick(page: str) -> list[str]:
    """Up to MAX_PHOTOS car photo names, best angles first."""
    names = [n for n in media_names(page) if is_car_photo(n)]
    return sorted(names, key=rank)[:MAX_PHOTOS]


def to_jpeg(data: bytes) -> bytes:
    """Convert any image bytes (webp, png) to JPEG quality 80."""
    img = Image.open(io.BytesIO(data)).convert("RGB")
    out = io.BytesIO()
    img.save(out, "JPEG", quality=80)
    return out.getvalue()


ROOT = Path(__file__).resolve().parents[2] / "data" / "car_images"
SLUG_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def load(slug: str, root: Path | None = None) -> list[bytes]:
    """Saved JPEG photos of one car, in order; empty if none or bad slug."""
    if not SLUG_RE.match(slug):
        return []
    base = root or ROOT
    files = [base / slug / f"{n}.jpg" for n in range(1, MAX_PHOTOS + 1)]
    return [f.read_bytes() for f in files if f.is_file()]
