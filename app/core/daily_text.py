"""ساخت خروجی قیمت روز (متن و جدول) و جمع‌کردن ردیف‌ها. بدون تلگرام."""
from html import escape

from app.core import ref_import

CHUNK_CHARS = 3800


def merge_rows(old: list[dict], new: list[dict]) -> list[dict]:
    """ردیف‌های سالم را اضافه می‌کند؛ تکراری (نام و سال) را با تازه‌تر عوض می‌کند."""
    ready, _ = ref_import.split_rows(new)
    index = {(r["name"], r["year"]): i for i, r in enumerate(old)}
    for row in ready:
        key = (row["name"], row["year"])
        if key in index:
            old[index[key]] = row
        else:
            index[key] = len(old)
            old.append(row)
    return old


def _change(row: dict, up: str, down: str) -> str:
    value = row.get("change_m")
    if not value:
        return ""
    if value > 0:
        return up.format(n=f"{value:g}")
    return down.format(n=f"{-value:g}")


def build_text(rows: list[dict], date: str, texts) -> str:
    lines = [
        texts.LINE.format(
            name=r["name"], year=r["year"], price=f"{r['price_m']:,}",
            change=_change(r, texts.CHANGE_UP, texts.CHANGE_DOWN),
        )
        for r in rows
    ]
    return texts.HEAD.format(date=date) + "\n".join(lines) + "\n" + texts.FOOT


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


def _html_row(row: dict, texts) -> str:
    change = _change(row, texts.CHANGE_UP, texts.CHANGE_DOWN).strip()
    values = (row["name"], row["year"], f"{row['price_m']:,}",
              change or texts.NO_VALUE)
    return "<tr>" + "".join(_cell("td", v) for v in values) + "</tr>"


def build_html(rows: list[dict], date: str, texts) -> str:
    head = "<tr>" + "".join(_cell("th", h) for h in texts.TBL_HEAD) + "</tr>"
    body = "".join(_html_row(r, texts) for r in rows)
    title = f"<p><b>{escape(texts.TBL_TITLE.format(date=date))}</b></p>"
    foot = f"<p>{escape(texts.FOOT.strip())}</p>"
    return title + "<table bordered striped>" + head + body + "</table>" + foot
