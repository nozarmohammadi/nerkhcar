"""متن پیش‌نویس جدول برای نمایش به ادمین."""
from app.adapters.telegram.texts import price_import as t
from app.core import ref_import

CHUNK = 25


def _flags(flags: list[str]) -> str:
    out = ""
    for marker, blocking in ((t.FLAG_BLOCK, True), (t.FLAG_INFO, False)):
        labels = [
            t.FLAG_LABELS[f] for f in flags
            if f in t.FLAG_LABELS and (f in ref_import.BLOCKING) == blocking
        ]
        if labels:
            out += marker + t.SEP.join(labels)
    return out


def _line(number: int, row: dict) -> str:
    price = t.NO_VALUE if row["price_m"] is None else f"{row['price_m']:,}"
    year = t.NO_VALUE if row["year"] is None else str(row["year"])
    return t.ROW.format(
        n=number, name=row["name"] or t.NO_VALUE, year=year,
        price=price, flags=_flags(row["flags"]),
    )


def draft_chunks(rows: list[dict], source: str) -> list[str]:
    title = t.DRAFT_TITLE.format(count=len(rows), source=source)
    if not rows:
        return [title + "\n\n" + t.EMPTY_DRAFT]
    lines = [_line(i, r) for i, r in enumerate(rows, start=1)]
    chunks = ["\n".join(lines[i:i + CHUNK]) for i in range(0, len(lines), CHUNK)]
    chunks[0] = title + "\n\n" + chunks[0]
    return chunks
