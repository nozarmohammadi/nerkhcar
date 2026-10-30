"""Car price button: new label, old label still accepted."""
from app.adapters.telegram.texts import menu

PRICE_TAG = "\U0001F3F7"
MONEY_BAG = "\U0001F4B0"


def test_new_label_uses_price_tag():
    assert menu.BTN_CAR_PRICE.startswith(PRICE_TAG)


def test_old_label_still_known():
    assert menu.BTN_CAR_PRICE_OLD.startswith(MONEY_BAG)
    assert menu.BTN_CAR_PRICE_OLD != menu.BTN_CAR_PRICE


def test_both_labels_listed_as_menu_buttons():
    assert menu.BTN_CAR_PRICE in menu.MENU_BUTTONS
    assert menu.BTN_CAR_PRICE_OLD in menu.MENU_BUTTONS


def test_same_words_after_the_emoji():
    new_words = menu.BTN_CAR_PRICE.split(" ", 1)[1]
    old_words = menu.BTN_CAR_PRICE_OLD.split(" ", 1)[1]
    assert new_words == old_words


def test_other_buttons_unchanged():
    assert menu.BTN_FX_GOLD.startswith("\U0001F4B5")
    assert menu.BTN_MY_CAR.startswith("\U0001F9EE")
