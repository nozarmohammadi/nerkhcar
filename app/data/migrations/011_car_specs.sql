-- Technical specs per trim, fetched once from an external source and kept forever.
CREATE TABLE IF NOT EXISTS car_specs (
    trim_id INTEGER PRIMARY KEY REFERENCES trims(id),
    source TEXT NOT NULL,
    source_slug TEXT NOT NULL,
    source_url TEXT NOT NULL,
    specs_json TEXT NOT NULL,
    reviewed INTEGER NOT NULL DEFAULT 0 CHECK (reviewed IN (0, 1)),
    fetched_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_car_specs_slug ON car_specs(source_slug);
