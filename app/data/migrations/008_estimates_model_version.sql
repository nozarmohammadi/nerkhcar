-- A10: store the estimate model version with every logged estimate.
ALTER TABLE estimates_log ADD COLUMN model_version TEXT;
