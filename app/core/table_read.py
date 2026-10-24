"""خواندن جدول از عکس: امتحان مدل‌ها به ترتیب و ساخت ردیف‌های نرمال‌شده."""
from collections.abc import Awaitable, Callable

from app.core import table_parse

Extractor = Callable[[bytes, str, str], Awaitable[tuple[str, str]]]


async def read_table(
    extractor: Extractor, image: bytes, mime: str, models: tuple[str, ...]
) -> tuple[str, list[dict]]:
    """نتیجه: (وضعیت، ردیف‌ها). وضعیت ok یعنی موفق."""
    last = "no_model"
    for model in models:
        status, text = await extractor(image, mime, model)
        if status != "ok":
            last = status
            continue
        rows = table_parse.parse_response(text)
        if rows:
            return "ok", table_parse.normalize_rows(rows)
        last = "bad_reply"
    return last, []
