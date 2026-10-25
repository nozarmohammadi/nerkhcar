CREATE TABLE published_daily (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  day TEXT NOT NULL,
  rows_json TEXT NOT NULL,
  published_at TEXT NOT NULL DEFAULT (datetime('now'))
);
