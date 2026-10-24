"""تبدیل پاسخ هوش مصنوعی به ردیف‌های جدول. بدون تلگرام و بدون شبکه."""
import json
import re

TICKS = "`" * 3
DIGITS = {base + i: str(i) for base in (0x06F0, 0x0660) for i in range(10)}
SEPARATORS = re.compile(r"[,/\s\u066c\u060c]")
FENCE = re.compile("^" + TICKS + "(?:json)?|" + TICKS + "$", re.M)
MILLION = 1_000_000
MAX_ROWS = 60
MAX_NAME = 40
PRICE_RANGE = (100, 30000)  # in million toman


def to_int(value) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        try:
            return int(value)
        except (ValueError, OverflowError):
            return None
    text = SEPARATORS.sub("", str(value).translate(DIGITS))
    return int(text) if re.fullmatch(r"-?\d+", text) else None


def parse_response(text: str) -> list | None:
    cleaned = FENCE.sub("", text.strip()).strip()
    try:
        data = json.loads(cleaned)
    except ValueError:
        return None
    if isinstance(data, dict):
        data = next((v for v in data.values() if isinstance(v, list)), None)
    return data if isinstance(data, list) and data else None


def _name(raw: dict, flags: list) -> str:
    name = " ".join(f"{raw.get('name') or ''} {raw.get('note') or ''}".split())
    if len(name) > MAX_NAME:
        flags.append("long_name")
        name = name[:MAX_NAME].rstrip()
    if not name:
        flags.append("no_name")
    return name


def _year(raw: dict, flags: list) -> int | None:
    year = to_int(raw.get("year"))
    if year is None:
        flags.append("no_year")
    elif 1990 <= year <= 2100:
        flags.append("greg_year")
    elif not 1380 <= year <= 1500:
        flags.append("bad_year")
    return year


def _price(raw: dict, flags: list) -> int | None:
    price = to_int(raw.get("price"))
    if price is None:
        flags.append("no_price")
        return None
    if price % MILLION:
        flags.append("rounded")
    value = round(price / MILLION)
    if not PRICE_RANGE[0] <= value <= PRICE_RANGE[1]:
        flags.append("range")
    return value


def _change(raw: dict) -> float | None:
    change = to_int(raw.get("change"))
    return None if change is None else round(change / MILLION, 1)


def normalize_row(raw) -> dict:
    if not isinstance(raw, dict):
        return {"name": "", "year": None, "price_m": None,
                "change_m": None, "flags": ["bad_row"]}
    flags: list[str] = []
    return {
        "name": _name(raw, flags),
        "year": _year(raw, flags),
        "price_m": _price(raw, flags),
        "change_m": _change(raw),
        "flags": flags,
    }


def normalize_rows(rows: list) -> list[dict]:
    return [normalize_row(r) for r in rows[:MAX_ROWS]]
