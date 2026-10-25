"""Parser test against the real tgju row shape (quoted '>' in data-title)."""
from app.core import fx_parse

REAL = (
    '<tr data-market-nameslug="price_dollar_rl" '
    'data-market-row="price_dollar_rl" '
    "data-title=\"<div class='tooltip-row'><span>x</span></div><hr>\" "
    'data-price="2,706,050">\n'
    '    <th><span class="mini-flag"></span>Dollar</th>'
    '<td class="nf">2,706,050</td></tr>'
)
SIMPLE = '<tr data-market-row="geram18" data-price="1,000"><th>Gold</th></tr>'
OTHER = '<tr data-market-row="price_gbp" data-price="5,000"><th>Pound</th></tr>'
NOPRICE = '<tr data-market-row="nim"><th>Half</th></tr>'


def test_real_row_with_gt_inside_attribute():
    rows = fx_parse.parse_page(REAL)
    assert rows["price_dollar_rl"] == {"title": "Dollar", "toman": 270605}


def test_simple_row_still_works():
    assert fx_parse.parse_page(SIMPLE)["geram18"]["toman"] == 100


def test_unwanted_and_priceless_rows_ignored():
    assert fx_parse.parse_page(OTHER + NOPRICE) == {}


def test_merge_first_page_wins():
    merged = fx_parse.parse_pages([SIMPLE, SIMPLE.replace("1,000", "9,000")])
    assert merged["geram18"]["toman"] == 100
