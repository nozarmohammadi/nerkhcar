"""Map body-part selections to the estimate engine categories."""

REPAINT_PARTS = {
    "hood", "front_left_door", "front_right_door",
    "rear_left_door", "rear_right_door", "trunk",
    "front_fender", "rear_fender",
}
REPLACED_PARTS = {
    "front_left_door", "front_right_door",
    "rear_left_door", "rear_right_door", "hood", "trunk",
}


def classify(mode: str | None, parts: list[str] | None) -> str:
    """Return the engine body category for selected damage."""
    if mode == "unknown":
        return "unknown"
    selected = set(parts or [])
    if not selected:
        return "clean"
    if mode == "replaced":
        return "repaint_or_replaced"
    if mode == "repaint":
        return "spots_many" if len(selected) > 2 else "spots_1_2"
    return "unknown"
