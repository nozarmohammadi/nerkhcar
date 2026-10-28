-- Daily history of published auto prices (one row per day/model/year).
CREATE TABLE IF NOT EXISTS price_daily (
    day TEXT NOT NULL,
    name TEXT NOT NULL,
    year INTEGER NOT NULL,
    price_m INTEGER NOT NULL,
    recorded_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (day, name, year)
);
CREATE INDEX IF NOT EXISTS idx_price_daily_model
    ON price_daily(name, year, day);
