CREATE TABLE used_base (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trim_id INTEGER NOT NULL REFERENCES trims(id),
  year INTEGER NOT NULL,
  price INTEGER NOT NULL CHECK (price > 0),
  samples INTEGER NOT NULL CHECK (samples >= 0),
  liquidity TEXT NOT NULL DEFAULT 'B' CHECK (liquidity IN ('A','B','C')),
  entered_by INTEGER,
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (trim_id, year)
);
