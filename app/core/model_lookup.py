"""Find car models and prices in the published daily table (pure logic)."""

PAGE_SIZE = 8


def model_names(rows: list[dict]) -> list[str]:
    """Unique model names, sorted alphabetically."""
    return sorted({r["name"] for r in rows})


def page_count(names: list[str], size: int = PAGE_SIZE) -> int:
    return max(1, -(-len(names) // size))


def page_of(names: list[str], page: int, size: int = PAGE_SIZE) -> list[tuple[int, str]]:
    """(index in full list, name) pairs for one page; page starts at 0."""
    start = max(page, 0) * size
    return list(enumerate(names))[start:start + size]


def years_of(rows: list[dict], name: str) -> list[int]:
    """Model years of this name found in the table, newest first."""
    found = {r["year"] for r in rows if r["name"] == name and r["year"]}
    return sorted(found, reverse=True)


def newest_price(rows: list[dict], name: str) -> tuple[int, float] | None:
    """(year, price in million toman) of the newest row of this model."""
    years = years_of(rows, name)
    if not years:
        return None
    for r in rows:
        if r["name"] == name and r["year"] == years[0]:
            return years[0], r["price_m"]
    return None


def price_for(rows: list[dict], name: str, year: int) -> tuple[float, bool] | None:
    """(daily price, exact) for the model and year.

    exact is False when this year is not in the table and the newest
    year of the model is used instead.
    """
    for r in rows:
        if r["name"] == name and r["year"] == year:
            return r["price_m"], True
    newest = newest_price(rows, name)
    return None if newest is None else (newest[1], False)
