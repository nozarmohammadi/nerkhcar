CREATE TABLE ai_usage (
  day TEXT PRIMARY KEY,
  count INTEGER NOT NULL DEFAULT 0,
  last_at TEXT
);
