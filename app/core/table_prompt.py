"""دستور (prompt) خواندن جدول قیمت خودرو از عکس."""

PROMPT = (
    "You read a screenshot of an Iranian car market price table. "
    "Columns (right to left): car name, model year, market price in toman, "
    "change versus the previous day. Return ONLY a JSON array. "
    "One object per table row with these keys: "
    "name (string exactly as printed, Persian letters), "
    "year (integer exactly as printed), "
    "price (integer, FULL toman, digits only, null if the cell is empty), "
    "change (integer toman: positive if green or up, negative if red or down, "
    "0 if unchanged, null if empty), "
    "note (small sub-label under the name, otherwise an empty string). "
    "Convert Persian digits to ASCII digits. "
    "The word for million means multiply by 1,000,000. "
    "Never guess a missing cell; use null. Skip the header, logos and captions."
)
