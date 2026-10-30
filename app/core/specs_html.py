"""Build the native-table html and plain text of one car's specs."""
import json
import re
from functools import lru_cache
from html import escape
from pathlib import Path

from app.core import daily_text


NBSP = "\u00a0"


@lru_cache(maxsize=1)
def _cfg() -> dict:
    """Load shortening rules (units, series separator) from the data file."""
    path = Path(__file__).resolve().parents[1] / "data" / "spec_shorten.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _move_unit(label: str, value: str, units: list) -> tuple[str, str]:
    """Move a trailing unit word from the value into the label."""
    for u in units:
        if value.endswith(" " + u):
            return f"{label} ({u})", value[: -len(u) - 1].replace(" × ", "×")
    return label, value


def _short_series(value: str, cfg: dict) -> str:
    """Turn 'generation + from year N' into 'generation, N'."""
    sep = cfg["series_sep"]
    if sep not in value:
        return value
    head, year = value.rsplit(sep, 1)
    return head + cfg["series_join"] + year


def compact(pairs: list) -> list:
    """Shorten long left-column texts so they fit on one line."""
    cfg = _cfg()
    out = []
    for a, b in pairs:
        a, b = _move_unit(a, str(b), cfg["units"])
        out.append((a, _short_series(b, cfg)))
    return out


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
        for a, b in compact(pairs)
    )
    table = "<table bordered striped>" + top + body + "</table>"
    cover = f'<img src="tg://photo?id={banner_id}"/>' if banner_id else ""
    return cover + slides(photo_ids) + table


def build_text(title: str, pairs: list[tuple[str, str]]) -> str:
    """Plain-text fallback with the same content."""
    lines = [f"{a}: {daily_text.fa(b)}" for a, b in pairs]
    return title + "\n\n" + "\n".join(lines)
