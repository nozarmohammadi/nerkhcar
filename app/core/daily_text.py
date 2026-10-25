"""ساخت خروجی قیمت روز (متن و جدول) و جمع‌کردن ردیف‌ها. بدون تلگرام."""
from collections import Counter
from datetime import date, datetime
from zoneinfo import ZoneInfo
from html import escape

from app.core import jalali, ref_import

CHUNK_CHARS = 3800


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


def _cell(tag: str, value) -> str:
    return f"<{tag}>{escape(str(value))}</{tag}>"


def _html_row(cell: tuple, texts) -> str:
    values = cell[:4]
    cells = [_cell("td", v) for v in values]
    return "<tr>" + "".join(cells) + "</tr>"


def build_html(
    rows: list[dict], day_text: str, texts, now: datetime | None = None
) -> str:
    from app.core import daily_cols
    head = "<tr>" + "".join(_cell("th", h) for h in texts.TBL_HEAD) + "</tr>"
    body = "".join(_html_row(c, texts) for c in daily_cols.cells(rows, texts))
    top = (
        f"<p><b>{escape(texts.TBL_TITLE)}</b></p>"
        f"<p>{escape(texts.DATE_LINE.format(date=day_text, time=time_text(texts, now)))}</p>"
        f"<p>{escape(texts.UNIT)}</p>"
    )
    foot = f"<p>{escape(texts.FOOT.strip())}</p>"
    table = "<table bordered striped compact>" + head + body + "</table>"
    return top + table + foot


def group_rows(rows: list[dict]) -> list[list[dict]]:
    """Split rows into one list per source photo, in photo order."""
    groups: dict[int, list[dict]] = {}
    for row in rows:
        groups.setdefault(row.get("photo") or 0, []).append(row)
    return [groups[key] for key in sorted(groups)]
