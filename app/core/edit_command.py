"""خواندن فرمان ویرایش پیش‌نویس (شماره، فیلد، مقدار). بدون تلگرام."""
from app.core import table_parse


def parse_edit(text: str, keywords: dict[str, str]) -> tuple[int, str, str] | None:
    parts = text.split(None, 2)
    if len(parts) < 2:
        return None
    number = table_parse.to_int(parts[0])
    field = keywords.get(parts[1])
    if number is None or field is None:
        return None
    value = parts[2].strip() if len(parts) > 2 else ""
    return number, field, value
