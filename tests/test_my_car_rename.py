"""Third menu button was renamed; the old label must keep working."""
from app.adapters.telegram.texts import menu


def test_new_label_uses_calculator_emoji():
    assert menu.BTN_MY_CAR.startswith("\U0001F9EE")


def test_old_label_still_in_menu_buttons():
    assert menu.BTN_MY_CAR_OLD.startswith("\U0001F697")
    assert menu.BTN_MY_CAR_OLD != menu.BTN_MY_CAR
    assert menu.BTN_MY_CAR_OLD in menu.MENU_BUTTONS
    assert menu.BTN_MY_CAR in menu.MENU_BUTTONS
