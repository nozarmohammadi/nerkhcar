"""تست ابزار چک قوانین و منوی ربات."""
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def test_check_rules_passes():
    result = subprocess.run(
        [sys.executable, str(BASE / "tools" / "check_rules.py")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout


def test_main_menu_has_three_buttons():
    from app.adapters.telegram.keyboards.main_menu import main_menu
    assert len(main_menu().keyboard) == 3
