"""ساخت خروجی قیمت روز (متن و جدول) و جمع‌کردن ردیف‌ها. بدون تلگرام."""
from collections import Counter
from datetime import date, datetime
from zoneinfo import ZoneInfo
from html import escape

from app.core import jalali, ref_import

CHUNK_CHARS = 3800
MIN_NAME = 16


def merge_rows(
    old: list[dict], new: list[dict], photo: int | None = None
) -> list[dict]:
    """ردیف‌های سالم را اضافه می‌کند؛ تکراری (نام و سال) را با تازه‌تر عوض می‌کند."""
    ready, _ = ref_import.split_rows(new)
    index = {(r["name"], r["year"]): i for i, r in enumerate(old)}
    for row in ready:
        if photo is not None:
            row["photo"] = photo
        key = (row["name"], row["year"])
        if key in index:
            old[index[key]] = row
        else:
            index[key] = len(old)
            old.append(row)
    return old


def date_text(texts, today: date | None = None) -> str:
    """تاریخ شمسی با رقم فارسی، مثل «۲ آبان ۱۴۰۵»."""
    today = today or date.today()
    jy, jm, jd = jalali.to_jalali(today.year, today.month, today.day)
    text = f"{jd} {texts.MONTHS[jm - 1]} {jy}"
    return text.translate(str.maketrans("0123456789", texts.DIGITS))


def time_text(texts, now: datetime | None = None) -> str:
    """ساعت به وقت تهران با رقم فارسی، مثل «۱۵:۴۲»."""
    now = now or datetime.now(ZoneInfo("Asia/Tehran"))
    return f"{now:%H:%M}".translate(str.maketrans("0123456789", texts.DIGITS))


_FA = {ord(str(i)): chr(0x06F0 + i) for i in range(10)}
_FA[ord(".")] = "\u066b"


def fa(value) -> str:
    """Latin digits to Persian digits; the thousands comma stays as is."""
    return str(value).translate(_FA)


def _main_year(rows: list[dict]):
    common = Counter(r["year"] for r in rows).most_common(1)
    return common[0][0] if common else None


def _label(row: dict, main_year) -> str:
    if row["year"] == main_year:
        return row["name"]
    return f"{row['name']} {row['year']}"


def _change(row: dict, up: str, down: str) -> str:
    value = row.get("change_m")
    if not value:
        return ""
    if value > 0:
        return up.format(n=fa(f"{value:g}"))
    return down.format(n=fa(f"{-value:g}"))


def build_text(rows: list[dict], day_text: str, texts) -> str:
    main = _main_year(rows)
    lines = [
        texts.LINE.format(
            label=_label(r, main), price=fa(f"{r['price_m']:,}"),
            change=_change(r, texts.CHANGE_UP, texts.CHANGE_DOWN),
        )
        for r in rows
    ]
    return texts.HEAD.format(date=day_text) + "\n".join(lines) + "\n" + texts.FOOT


def text_chunks(text: str) -> list[str]:
    """متن بلند را به تکه‌های کوتاه‌تر از سقف تلگرام می‌شکند."""
    chunks, current = [], ""
    for line in text.split("\n"):
        if current and len(current) + len(line) + 1 > CHUNK_CHARS:
            chunks.append(current)
            current = line
        else:
            current = current + "\n" + line if current else line
    if current:
        chunks.append(current)
    return chunks


ROWS_PER_MESSAGE = 50


def _cell(tag: str, value, align: str = "") -> str:
    attr = f' align="{align}"' if align else ""
    return f"<{tag}{attr}>{escape(str(value))}</{tag}>"


def _html_row(cell: tuple, texts) -> str:
    values = cell[:4]
    pad = "&nbsp;" * max(0, MIN_NAME - len(str(values[0])))
    cells = [f"<td>{escape(str(values[0]))}{pad}</td>"]
    cells += [_cell("td", v) for v in values[1:3]]
    cells.append(_cell("td", values[3], "center"))
    return "<tr>" + "".join(cells) + "</tr>"


def _table(cells: list, texts) -> str:
    heads = [_cell("th", h) for h in texts.TBL_HEAD[:3]]
    heads.append(_cell("th", texts.TBL_HEAD[3], "center"))
    body = "".join(_html_row(c, texts) for c in cells)
    return "<table bordered striped><tr>" + "".join(heads) + "</tr>" + body + "</table>"


def build_html_chunks(
    rows: list[dict], day_text: str, texts, now: datetime | None = None,
    size: int = ROWS_PER_MESSAGE,
) -> list[str]:
    """One HTML per message; rows without a price are never shown."""
    from app.core import daily_cols
    cells = daily_cols.cells([r for r in rows if r.get("price_m")], texts)
    parts = [cells[i:i + size] for i in range(0, len(cells), size)] or [[]]
    when = texts.DATE_LINE.format(date=day_text, time=time_text(texts, now))
    top = (
        f"<p><b>{escape(texts.TBL_TITLE)}</b></p>"
        f"<p>{escape(when)}</p><p>{escape(texts.UNIT)}</p>"
    )
    foot = f"<p>{escape(texts.FOOT.strip())}</p>"
    return [
        (top if i == 0 else "") + _table(part, texts)
        + (foot if i == len(parts) - 1 else "")
        for i, part in enumerate(parts)
    ]


def build_html(
    rows: list[dict], day_text: str, texts, now: datetime | None = None
) -> str:
    """The whole table as one HTML (small tables and old callers)."""
    return build_html_chunks(rows, day_text, texts, now, max(len(rows), 1))[0]


def group_rows(rows: list[dict]) -> list[list[dict]]:
    """Split rows into one list per source photo, in photo order."""
    groups: dict[int, list[dict]] = {}
    for row in rows:
        groups.setdefault(row.get("photo") or 0, []).append(row)
    return [groups[key] for key in sorted(groups)]
