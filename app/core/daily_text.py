"""ساخت خروجی متن قیمت روز و جمع‌کردن ردیف‌ها. بدون تلگرام."""
from app.core import ref_import


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
    return up.format(n=value) if value > 0 else down.format(n=-value)


def build_text(rows: list[dict], date: str, texts) -> str:
    lines = [
        texts.LINE.format(
            name=r["name"], year=r["year"], price=f"{r['price_m']:,}",
            change=_change(r, texts.CHANGE_UP, texts.CHANGE_DOWN),
        )
        for r in rows
    ]
    return texts.HEAD.format(date=date) + "\n".join(lines) + "\n" + texts.FOOT
