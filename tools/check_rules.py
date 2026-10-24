"""چک خودکار قوانین کد. خروجی 0 یعنی همه‌چیز درست است."""
import ast
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
MAX_FILE = 200
MAX_FUNC = 30
PERSIAN = re.compile(r"[\u0600-\u06FF]")
SKIP_DIRS = {"venv", "data", "backups", "logs", ".git", "__pycache__"}


def py_files() -> list[Path]:
    return [
        p for p in BASE.rglob("*.py")
        if not SKIP_DIRS & set(p.relative_to(BASE).parts)
    ]


def check_size(path: Path, lines: list[str]) -> list[str]:
    if len(lines) > MAX_FILE:
        return [f"{path.name}: {len(lines)} خط (حد {MAX_FILE})"]
    return []


def check_funcs(path: Path, tree: ast.AST) -> list[str]:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            size = node.end_lineno - node.lineno + 1
            if size > MAX_FUNC:
                out.append(f"{path.name}:{node.name}: {size} خط (حد {MAX_FUNC})")
    return out


def _imported_names(tree: ast.AST) -> dict[str, int]:
    names = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                names[(a.asname or a.name).split(".")[0]] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                names[a.asname or a.name] = node.lineno
    return names


def check_unused(path: Path, tree: ast.AST) -> list[str]:
    if path.name == "__init__.py":
        return []
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    used |= {n.value.id for n in ast.walk(tree)
             if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)}
    return [f"{path.name}:{ln}: import بی‌استفاده «{n}»"
            for n, ln in _imported_names(tree).items() if n not in used]


def check_core_pure(path: Path, text: str) -> list[str]:
    rel = path.relative_to(BASE).parts
    if rel[:2] == ("app", "core") and re.search(r"^\s*(from|import)\s+aiogram", text, re.M):
        return [f"{path.name}: core نباید aiogram را import کند"]
    return []


def check_persian(path: Path, text: str) -> list[str]:
    rel = path.relative_to(BASE).parts
    if "texts" in rel or "tests" in rel or "tools" in rel or "app" not in rel:
        return []
    bad = [i for i, ln in enumerate(text.splitlines(), 1)
           if PERSIAN.search(ln) and not ln.strip().startswith(("#", '"""'))
           and "log." not in ln and "raise" not in ln]
    return [f"{path.name}:{i}: متن فارسی بیرون از texts/" for i in bad]


def main() -> int:
    problems = []
    for path in py_files():
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        problems += check_size(path, text.splitlines())
        problems += check_funcs(path, tree)
        problems += check_unused(path, tree)
        problems += check_core_pure(path, text)
        problems += check_persian(path, text)
    for p in problems:
        print("❌", p)
    print("✅ همه قوانین رعایت شده" if not problems else f"{len(problems)} مشکل")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
