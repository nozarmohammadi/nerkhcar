"""Render the daily car price table as a PNG image. No Telegram imports."""
from datetime import datetime
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.core import daily_cols, daily_text

FONT_DIR = Path(__file__).resolve().parents[2] / "assets" / "fonts"
WIDTH = 1080
MIN_HEIGHT = 1080
PAD = 40
TOP_H = 220
HEAD_H = 72
ROW_H = 66
FOOT_H = 88
NAME_X = WIDTH - PAD - 24
NAME_W = 400
YEAR_X = 590
PRICE_X = 400
CHANGE_X = 160
BG = (244, 246, 251)
NAVY = (27, 42, 94)
WHITE = (255, 255, 255)
INK = (30, 36, 56)
MUTED = (96, 104, 124)
ROW_COLORS = ((221, 228, 244), (255, 246, 229))
UP = (24, 128, 56)
DOWN = (198, 40, 40)


@lru_cache(maxsize=64)
def _font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    name = "Vazirmatn-Bold.ttf" if bold else "Vazirmatn-Regular.ttf"
    return ImageFont.truetype(
        str(FONT_DIR / name), size, layout_engine=ImageFont.Layout.RAQM)


def _text(draw, xy, text, font, fill, anchor, direction="rtl") -> None:
    draw.text(xy, text, font=font, fill=fill, anchor=anchor,
              direction=direction, language="fa")


def _fit(draw, text: str, size: int, max_w: int):
    """Largest regular font (down to 18 px) whose text fits max_w."""
    while size > 18:
        font = _font(False, size)
        width = draw.textlength(
            text, font=font, direction="rtl", language="fa")
        if width <= max_w:
            return font
        size -= 2
    return _font(False, 18)


def _draw_top(draw, day_text: str, texts, now) -> None:
    date_line = texts.IMG_DATE.format(
        date=day_text, time=daily_text.time_text(texts, now))
    cx = WIDTH // 2
    _text(draw, (cx, 70), texts.IMG_TITLE, _font(True, 58), NAVY, "mm")
    _text(draw, (cx, 130), date_line, _font(False, 32), INK, "mm")
    _text(draw, (cx, 178), texts.UNIT, _font(False, 28), MUTED, "mm")


def _draw_head(draw, texts) -> None:
    draw.rounded_rectangle(
        [PAD, TOP_H, WIDTH - PAD, TOP_H + HEAD_H], radius=16, fill=NAVY,
        corners=(True, True, False, False))
    name, year, price, change = texts.TBL_HEAD
    mid = TOP_H + HEAD_H // 2
    font = _font(True, 32)
    _text(draw, (NAME_X, mid), name, font, WHITE, "rm")
    _text(draw, (YEAR_X, mid), year, font, WHITE, "mm")
    _text(draw, (PRICE_X, mid), price, font, WHITE, "mm")
    _text(draw, (CHANGE_X, mid), change, font, WHITE, "mm")


def _draw_row(draw, y: int, cells: tuple, index: int) -> None:
    label, year, price, change, direction = cells
    draw.rectangle(
        [PAD, y, WIDTH - PAD, y + ROW_H - 1], fill=ROW_COLORS[index % 2])
    mid = y + ROW_H // 2
    font = _fit(draw, label, 32, NAME_W)
    _text(draw, (NAME_X, mid), label, font, INK, "rm")
    _text(draw, (YEAR_X, mid), year, _font(True, 32), INK, "mm")
    _text(draw, (PRICE_X, mid), price, _font(True, 34), INK, "mm", "ltr")
    color = (MUTED, UP, DOWN)[direction]  # direction -1 picks DOWN
    _text(draw, (CHANGE_X, mid), change, _font(True, 32), color, "mm", "ltr")


def _draw_foot(draw, height: int, texts) -> None:
    _text(draw, (WIDTH // 2, height - FOOT_H // 2), texts.FOOT.strip(),
          _font(False, 28), MUTED, "mm")


def draw_frame(
    cells: list, shown: int, day_text: str, texts,
    now: datetime | None, height: int,
) -> Image.Image:
    """Draw header, the first `shown` rows and the footer on one canvas."""
    img = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(img)
    _draw_top(draw, day_text, texts, now)
    _draw_head(draw, texts)
    y = TOP_H + HEAD_H
    for index, row in enumerate(cells[:shown]):
        _draw_row(draw, y, row, index)
        y += ROW_H
    _draw_foot(draw, height, texts)
    return img


def render(
    rows: list[dict], day_text: str, texts, now: datetime | None = None
) -> bytes:
    """Return PNG bytes of the price table; height grows with row count."""
    cells = daily_cols.cells(rows, texts, image=True)
    height = max(MIN_HEIGHT, TOP_H + HEAD_H + ROW_H * len(cells) + FOOT_H)
    img = draw_frame(cells, len(cells), day_text, texts, now, height)
    out = BytesIO()
    img.save(out, "PNG", optimize=True)
    return out.getvalue()


def render_all(
    rows: list[dict], day_text: str, texts, now: datetime | None = None
) -> list[bytes]:
    """One PNG per source photo, so the slide count matches the photos sent."""
    return [
        render(group, day_text, texts, now)
        for group in daily_text.group_rows(rows)
    ]
