"""Draw a classy per-group brand banner image (pure logic)."""
import zlib
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.core import brand_groups

FONT = Path(__file__).resolve().parents[2] / "assets" / "fonts" / "Vazirmatn-Bold.ttf"
WIDTH, HEIGHT, LINE_H = 1080, 84, 3
MAX_TEXT = 640
FG = (255, 255, 255)
GAP, ARM, DIAMOND = 28, 140, 6
# (top, bottom, accent) per group index; the last one is the neutral theme.
THEMES = (
    ((10, 25, 60), (28, 68, 140), (212, 175, 55)),
    ((6, 44, 38), (16, 104, 84), (226, 196, 120)),
    ((70, 12, 24), (140, 32, 50), (240, 200, 140)),
    ((28, 30, 38), (66, 72, 90), (214, 64, 69)),
    ((20, 24, 70), (70, 70, 160), (150, 200, 255)),
    ((40, 18, 66), (92, 52, 140), (220, 190, 110)),
    ((16, 52, 72), (36, 120, 150), (255, 255, 255)),
    ((60, 36, 20), (120, 76, 44), (230, 200, 150)),
    ((10, 50, 90), (30, 110, 170), (255, 205, 60)),
    ((20, 30, 80), (150, 30, 40), (255, 255, 255)),
    ((30, 34, 40), (70, 76, 84), (170, 178, 190)),
)


@lru_cache(maxsize=16)
def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(
        str(FONT), size, layout_engine=ImageFont.Layout.RAQM)


def _width(draw: ImageDraw.ImageDraw, name: str, font) -> float:
    return draw.textlength(name, font=font, direction="rtl", language="fa")


def _fit(draw: ImageDraw.ImageDraw, name: str) -> ImageFont.FreeTypeFont:
    """Largest font (down to 22 px) whose text fits the banner."""
    size = 40
    while size > 22:
        font = _font(size)
        if _width(draw, name, font) <= MAX_TEXT:
            return font
        size -= 2
    return _font(22)


def _theme(index: int) -> tuple:
    return THEMES[index] if 0 <= index < len(THEMES) else THEMES[-1]


def theme_of(name: str, order: tuple) -> int:
    """Theme index of a group name; unknown names get the neutral theme."""
    return order.index(name) if name in order else len(THEMES) - 1


def _background(top: tuple, bottom: tuple, accent: tuple) -> Image.Image:
    """Vertical gradient with a thin accent line at the bottom."""
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        color = tuple(round(a + (b - a) * t) for a, b in zip(top, bottom))
        draw.line([(0, y), (WIDTH, y)], fill=color)
    draw.rectangle([0, HEIGHT - LINE_H, WIDTH, HEIGHT], fill=accent)
    return img


def _ornament(draw, edge: float, side: int, y: int, accent: tuple) -> None:
    """Accent line with a small diamond, placed beside the text."""
    start = edge + side * GAP
    draw.line([(start, y), (start + side * ARM, y)], fill=accent, width=2)
    d = DIAMOND
    draw.polygon(
        [(start, y - d), (start + d, y), (start, y + d), (start - d, y)],
        fill=accent)


def render(name: str, theme: int = -1) -> bytes:
    """Return PNG bytes: name centered between ornaments in a group theme."""
    top, bottom, accent = _theme(theme)
    img = _background(top, bottom, accent)
    draw = ImageDraw.Draw(img)
    font = _fit(draw, name)
    cx, cy = WIDTH // 2, (HEIGHT - LINE_H) // 2
    half = _width(draw, name, font) / 2
    draw.text((cx, cy), name, font=font, fill=FG, anchor="mm",
              direction="rtl", language="fa")
    for side in (-1, 1):
        _ornament(draw, cx + side * half, side, cy, accent)
    out = BytesIO()
    img.save(out, "PNG", optimize=True)
    return out.getvalue()


def banner_id(name: str) -> str:
    """Stable short id of a brand image inside one rich message."""
    return "b%08x" % zlib.crc32(name.encode("utf-8"))


def banners_in(
    html: str, rows: list[dict], other: str, order: tuple = ()
) -> dict[str, bytes]:
    """{id: PNG} for every brand banner referenced by this html."""
    shown = [r for r in rows if r.get("price_m")]
    out = {}
    for brand, _ in brand_groups.grouped(shown):
        if brand is None:
            continue
        name = brand or other
        key = banner_id(name)
        if key in html:
            out[key] = render(name, theme_of(name, order))
    return out
