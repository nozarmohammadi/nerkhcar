CREATE TABLE users (
  tg_id INTEGER PRIMARY KEY,
  first_seen TEXT NOT NULL DEFAULT (datetime('now')),
  last_seen TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE admins (
  tg_id INTEGER PRIMARY KEY,
  role TEXT NOT NULL CHECK (role IN ('owner','editor')),
  pw_hash TEXT,
  must_change INTEGER NOT NULL DEFAULT 1,
  failed_count INTEGER NOT NULL DEFAULT 0,
  locked_until TEXT,
  session_until TEXT,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  at TEXT NOT NULL DEFAULT (datetime('now')),
  admin_id INTEGER,
  action TEXT NOT NULL,
  detail TEXT NOT NULL DEFAULT ''
);
CREATE TABLE brands (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);
CREATE TABLE models (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  brand_id INTEGER NOT NULL REFERENCES brands(id),
  name TEXT NOT NULL,
  UNIQUE (brand_id, name)
);
CREATE TABLE trims (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  model_id INTEGER NOT NULL REFERENCES models(id),
  name TEXT NOT NULL,
  UNIQUE (model_id, name)
);
CREATE TABLE prices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trim_id INTEGER NOT NULL REFERENCES trims(id),
  year INTEGER NOT NULL,
  low INTEGER NOT NULL,
  high INTEGER NOT NULL,
  confidence TEXT NOT NULL CHECK (confidence IN ('green','yellow','orange','red')),
  status TEXT NOT NULL CHECK (status IN ('published','held','blocked')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  confirmed_at TEXT,
  entered_by INTEGER,
  UNIQUE (trim_id, year)
);
CREATE TABLE price_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  price_id INTEGER NOT NULL REFERENCES prices(id),
  low INTEGER NOT NULL,
  high INTEGER NOT NULL,
  at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE reference_prices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trim_id INTEGER NOT NULL REFERENCES trims(id),
  year INTEGER NOT NULL,
  source_name TEXT NOT NULL,
  low INTEGER NOT NULL,
  high INTEGER NOT NULL,
  entered_at TEXT NOT NULL DEFAULT (datetime('now')),
  entered_by INTEGER
);
CREATE TABLE fx_cache (
  symbol TEXT PRIMARY KEY,
  value REAL NOT NULL,
  source TEXT NOT NULL,
  fetched_at TEXT NOT NULL
);
CREATE TABLE estimates_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  at TEXT NOT NULL DEFAULT (datetime('now')),
  user_id INTEGER,
  answers TEXT NOT NULL,
  low INTEGER NOT NULL,
  high INTEGER NOT NULL
);
