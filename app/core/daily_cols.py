"""Table cells with a separate model-year column. No Telegram imports."""
from app.core import daily_text


def change_text(row: dict, texts) -> str:
    return daily_text._change(row, texts.CHANGE_UP, texts.CHANGE_DOWN).strip()


def year_text(row: dict, texts) -> str:
    year = row.get("year")
    return texts.NO_VALUE if year is None else daily_text.fa(year)


def cells(rows: list[dict], texts) -> list[tuple[str, str, str, str, int]]:
    """Cells: name, year, price, change text, direction (-1, 0, 1)."""
    out = []
    for row in rows:
        value = row.get("change_m") or 0
        change = change_text(row, texts)
        out.append((
            row["name"], year_text(row, texts),
            daily_text.fa(f"{row['price_m']:,}"),
            change or texts.NO_VALUE, (value > 0) - (value < 0),
        ))
    return out
