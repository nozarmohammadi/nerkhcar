"""Build the native-table html and plain text of one car's specs."""
from html import escape

from app.core import daily_text


def _cell(tag: str, value: str) -> str:
    return f"<{tag}>{escape(value)}</{tag}>"


def build_html(
    title: str, pairs: list[tuple[str, str]], head: tuple, banner_id: str = ""
) -> str:
    """Cover image (optional), then a two-column bordered table, Persian digits."""
    top = "<tr>" + "".join(_cell("th", h) for h in head) + "</tr>"
    body = "".join(
        "<tr>" + _cell("td", a) + _cell("td", daily_text.fa(b)) + "</tr>"
        for a, b in pairs
    )
    table = "<table bordered striped>" + top + body + "</table>"
    cover = f'<img src="tg://photo?id={banner_id}"/>' if banner_id else ""
    return cover + table


def build_text(title: str, pairs: list[tuple[str, str]]) -> str:
    """Plain-text fallback with the same content."""
    lines = [f"{a}: {daily_text.fa(b)}" for a, b in pairs]
    return title + "\n\n" + "\n".join(lines)
