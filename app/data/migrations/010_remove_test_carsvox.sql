-- Remove the test brand carsvox (7 test Jack models) with everything attached.
DELETE FROM price_history WHERE price_id IN (
  SELECT p.id FROM prices p JOIN trims t ON t.id = p.trim_id
  JOIN models m ON m.id = t.model_id JOIN brands b ON b.id = m.brand_id
  WHERE b.name = 'carsvox');
DELETE FROM prices WHERE trim_id IN (
  SELECT t.id FROM trims t JOIN models m ON m.id = t.model_id
  JOIN brands b ON b.id = m.brand_id WHERE b.name = 'carsvox');
DELETE FROM used_base WHERE trim_id IN (
  SELECT t.id FROM trims t JOIN models m ON m.id = t.model_id
  JOIN brands b ON b.id = m.brand_id WHERE b.name = 'carsvox');
DELETE FROM reference_prices WHERE trim_id IN (
  SELECT t.id FROM trims t JOIN models m ON m.id = t.model_id
  JOIN brands b ON b.id = m.brand_id WHERE b.name = 'carsvox');
DELETE FROM trims WHERE model_id IN (
  SELECT m.id FROM models m JOIN brands b ON b.id = m.brand_id
  WHERE b.name = 'carsvox');
DELETE FROM models WHERE brand_id IN (
  SELECT id FROM brands WHERE name = 'carsvox');
DELETE FROM brands WHERE name = 'carsvox';
