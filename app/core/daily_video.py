"""Plan and draw the daily price video frames. No Telegram imports."""
from datetime import datetime
from io import BytesIO
from typing import Iterator

from PIL import Image

from app.core import daily_cols, daily_image, daily_text

CANVAS_H = 1920
OUT_SIZE = (720, 1280)
PAGE_ROWS = (
    CANVAS_H - daily_image.TOP_H - daily_image.HEAD_H - daily_image.FOOT_H
) // daily_image.ROW_H
ROW_SEC = 0.35
START_SEC = 0.6
PAGE_START_SEC = 0.3
PAGE_HOLD_SEC = 1.2
END_HOLD_SEC = 3.0


def split_pages(groups: list[list]) -> list[list]:
    """One page per source photo; a group over PAGE_ROWS splits evenly."""
    pages = []
    for group in groups:
        if not group:
            continue
        count = -(-len(group) // PAGE_ROWS)
        size = -(-len(group) // count)
        pages += [group[i:i + size] for i in range(0, len(group), size)]
    return pages


def frame_plan(pages: list[list]) -> list[tuple[int, int, float]]:
    """Return (page index, rows shown, seconds) for every frame."""
    plan = []
    for p, page in enumerate(pages):
        plan.append((p, 0, START_SEC if p == 0 else PAGE_START_SEC))
        for shown in range(1, len(page) + 1):
            sec = ROW_SEC
            if shown == len(page):
                last = p == len(pages) - 1
                sec = END_HOLD_SEC if last else PAGE_HOLD_SEC
            plan.append((p, shown, sec))
    return plan


def _png(img: Image.Image) -> bytes:
    out = BytesIO()
    img.resize(OUT_SIZE, Image.Resampling.LANCZOS).save(out, "PNG")
    return out.getvalue()


def render_frames(
    rows: list[dict], day_text: str, texts, now: datetime | None = None
) -> Iterator[tuple[bytes, float]]:
    """Yield (PNG bytes, seconds) one frame at a time to keep memory low."""
    groups = [
        daily_cols.cells(group, texts, image=True)
        for group in daily_text.group_rows(rows)
    ]
    pages = split_pages(groups)
    for page, shown, seconds in frame_plan(pages):
        img = daily_image.draw_frame(
            pages[page], shown, day_text, texts, now, CANVAS_H)
        yield _png(img), seconds
