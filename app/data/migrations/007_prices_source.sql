ALTER TABLE prices
ADD COLUMN source TEXT NOT NULL DEFAULT 'photo'
CHECK (source IN ('auto', 'photo'));
