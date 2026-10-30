"""Pure logic for the specs button: grouping by slug prefix and rendering."""


def prefix(slug: str) -> str:
    """First part of a source slug, e.g. 'saipa-111' -> 'saipa'."""
    return str(slug).split("-")[0]


def names(groups: tuple, other: str) -> list[str]:
    """Group names by index; the last entry names the unmapped cars."""
    return [name for name, _ in groups] + [other]


def split(rows: list[dict], groups: tuple) -> list[list[dict]]:
    """Rows per group in group order; the last list holds unmapped rows."""
    lookup = {p: i for i, (_, prefixes) in enumerate(groups) for p in prefixes}
    out: list[list[dict]] = [[] for _ in range(len(groups) + 1)]
    for row in rows:
        out[lookup.get(prefix(row["slug"]), len(groups))].append(row)
    return out


def render(title: str, specs: dict, labels: tuple, line_fmt: str) -> str:
    """Title plus one line per label that has a non-empty value."""
    lines = [title, ""]
    for key, label in labels:
        value = str(specs.get(key) or "").strip()
        if value:
            lines.append(line_fmt.format(label=label, value=value))
    return "\n".join(lines)
