"""Persistence for user estimate results."""
import json
import sqlite3


def add(
    conn: sqlite3.Connection,
    user_id: int,
    answers: dict,
    result: dict,
) -> None:
    """Store the fair band and all computed bands as JSON."""
    fair_low, fair_high = result["fair"]
    payload = dict(answers)
    payload["bands"] = {
        key: list(result[key])
        for key in ("quick_sale", "fair", "listing")
    }
    conn.execute(
        "INSERT INTO estimates_log(user_id, answers, low, high) "
        "VALUES (?, ?, ?, ?)",
        (
            user_id,
            json.dumps(payload, ensure_ascii=False),
            round(fair_low),
            round(fair_high),
        ),
    )
    conn.commit()
