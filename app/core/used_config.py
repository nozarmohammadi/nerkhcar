"""Tunable factors for the used-car estimate (all values are assumptions)."""

CFG = {
    "current_year": 1405,
    "std_km_per_year": 20000,
    "min_expected_km": 10000,
    # (km / expected km, price factor); linear between points
    "mileage_curve": [
        (0.5, 1.02), (1.0, 1.00), (1.5, 0.94),
        (2.0, 0.86), (2.5, 0.78), (3.0, 0.72),
    ],
    "body": {
        "clean": 1.00, "spots_1_2": 0.95, "spots_many": 0.88,
        "repaint_or_replaced": 0.78, "unknown": 0.92,
    },
    "chassis": {
        "healthy": 1.00, "minor_fixed": 0.90, "major": 0.75,
        "unknown": 0.95,
    },
    "second_damage_weight": 0.5,
    "color": {"white": 1.00, "dark_silver": 0.98, "other": 0.95},
    "total_floor": 0.55,
    "total_cap": 1.05,
    "freshness": {"fresh_hours": 24, "max_hours": 72, "stale_spread_mult": 1.5},
    "spread": {"base": 0.04, "unknown_answer_add": 0.02, "illiquid_mult": 2.0},
    "min_samples_per_base": 3,
    "limits": {"max_km": 1500000},
    "zero_ref": {"warn_max_age": 3, "warn_spread_mult": 1.5,
                 "fallback_spread_mult": 2.0},
}
