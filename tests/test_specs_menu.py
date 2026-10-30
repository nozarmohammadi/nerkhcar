"""Tests that the specs button is wired into the menu and router order."""
from app import main
from app.adapters.telegram.keyboards import main_menu
from app.adapters.telegram.texts import menu


def test_button_in_menu_buttons():
    assert menu.BTN_SPECS in menu.MENU_BUTTONS


def test_button_on_main_keyboard():
    kb = main_menu.main_menu()
    texts = [b.text for row in kb.keyboard for b in row]
    assert menu.BTN_SPECS in texts


def test_specs_router_before_menu_stub():
    names = [m.__name__.rsplit(".", 1)[-1] for m in main.ROUTER_MODULES]
    assert names.index("specs") < names.index("menu_stub")
