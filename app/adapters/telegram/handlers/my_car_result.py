"""My car: final step helpers (pick trim, compute estimate, log it)."""
from app.adapters.telegram import dbrun
from app.adapters.telegram.texts import my_car as t
from app.config import Settings
from app.core import my_car_calc, my_car_view
from app.data import repo_estimates, repo_prices, repo_published


def best_trim(conn, answers: dict):
    """Return (trim_id, price) for the chosen model and year.

    Prefers a trim of the model that has a price for the year; otherwise
    falls back to the trim stored in the answers (the first one).
    """
    for row in answers.get("catalog", []):
        if row["model"] != answers.get("name"):
            continue
        price = repo_prices.get_price(conn, row["trim_id"], answers["year"])
        if price is not None:
            return row["trim_id"], price
    stored = answers.get("trim_id")
    if stored is None:
        return None, None
    return stored, repo_prices.get_price(conn, stored, answers["year"])


def finish(settings: Settings, user_id: int, answers: dict) -> str:
    """Compute the estimate, log it, and return the text to show."""
    data = dbrun.run(settings, repo_published.get)
    trim_id, price = dbrun.run(settings, lambda conn: best_trim(conn, answers))
    answers = {**answers, "trim_id": trim_id}
    zero = None if price is None else price.low
    result = my_car_calc.compute(data, answers, zero=zero)
    if result["status"] != "ok":
        return t.NO_DATA
    dbrun.run(
        settings, lambda conn: repo_estimates.add(conn, user_id, answers, result)
    )
    return my_car_view.build_text(result, answers["name"], answers["year"], t)
