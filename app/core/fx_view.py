"""Build the FX table (html and plain text) and judge staleness. No Telegram."""
from datetime import datetime, timedelta, timezone
from html import escape

from app.core import daily_text

FMT = "%Y-%m-%d %H:%M:%S"
MAX_AGE_MIN = 5


def _parse(stamp: str) -> datetime:
    return datetime.strptime(stamp, FMT).replace(tzinfo=timezone.utc)


def oldest_stamp(rows: list[dict]) -> str:
    """The oldest fetch time among the rows (UTC text)."""
    return min(r["fetched_at"] for r in rows)


def is_stale(rows: list[dict], expected: int, now: datetime) -> bool:
    """True if rows are incomplete or older than MAX_AGE_MIN minutes."""
    if len(rows) < expected:
        return True
    age = now - _parse(oldest_stamp(rows))
    return age > timedelta(minutes=MAX_AGE_MIN)


def table_rows(rows: list[dict], texts) -> list[tuple[str, str]]:
    """Pairs of (label, price with Persian digits)."""
    return [
        (texts.LABELS[r["symbol"]], daily_text.fa(f"{r['toman']:,}"))
        for r in rows
    ]


def _cell(tag: str, value: str) -> str:
    return f"<{tag}>{escape(value)}</{tag}>"


def build_html(rows, day_line: str, texts) -> str:
    """Native table message; day_line is the ready date and time line."""
    head = "<tr>" + "".join(_cell("th", h) for h in texts.HEAD) + "</tr>"
    body = "".join(
        "<tr>" + _cell("td", a) + _cell("td", b) + "</tr>"
        for a, b in table_rows(rows, texts)
    )
    top = (
        f"<p><b>{escape(texts.TITLE)}</b></p><p>{escape(day_line)}</p>"
        f"<p>{escape(texts.UNIT)}</p>"
    )
    table = "<table bordered striped>" + head + body + "</table>"
    return top + table + f"<p>{escape(texts.FOOT)}</p>"


def build_text(rows, day_line: str, texts) -> str:
    """Plain-text fallback with the same content."""
    lines = [
        texts.LINE.format(label=a, price=b) for a, b in table_rows(rows, texts)
    ]
    head = f"{texts.TITLE}\n{day_line}\n{texts.UNIT}\n"
    return head + "\n".join(lines) + "\n" + texts.FOOT
