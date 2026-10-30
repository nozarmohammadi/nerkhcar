"""Build the native-table html and plain text of one car's specs."""
import re
from html import escape

from app.core import daily_text


NBSP = "\u00a0"


def glue(text: str) -> str:
    """Keep a year with its word and a number with its unit on one line."""
    text = re.sub(r"(\S) (\d+)$", "\\1" + NBSP + "\\2", text)
    return re.sub(r"(\d) (\S+)$", "\\1" + NBSP + "\\2", text)


def _cell(tag: str, value: str) -> str:
    return f"<{tag}>{escape(value)}</{tag}>"


def slides(photo_ids: tuple) -> str:
    """Slideshow block of photos, or empty when there are none."""
    if not photo_ids:
        return ""
    imgs = "".join(f'<img src="tg://photo?id={i}"/>' for i in photo_ids)
    return "<tg-slideshow>" + imgs + "</tg-slideshow>"


def build_html(
    title: str, pairs: list[tuple[str, str]], head: tuple,
    banner_id: str = "", photo_ids: tuple = (),
) -> str:
    """Cover image (optional), then a two-column bordered table, Persian digits."""
    top = "<tr>" + "".join(_cell("th", h) for h in head) + "</tr>"
    body = "".join(
        "<tr>" + _cell("td", a) + _cell("td", glue(daily_text.fa(b))) + "</tr>"
        for a, b in pairs
    )
    table = "<table bordered striped>" + top + body + "</table>"
    cover = f'<img src="tg://photo?id={banner_id}"/>' if banner_id else ""
    return cover + slides(photo_ids) + table


def build_text(title: str, pairs: list[tuple[str, str]]) -> str:
    """Plain-text fallback with the same content."""
    lines = [f"{a}: {daily_text.fa(b)}" for a, b in pairs]
    return title + "\n\n" + "\n".join(lines)
