"""Build transparent search queries for configured contribution areas."""


def build_issue_queries(areas: tuple[str, ...], labels: tuple[str, ...]) -> tuple[str, ...]:
    """Return stable, de-duplicated area/label query combinations."""

    normalized_areas = tuple(dict.fromkeys(area.strip() for area in areas if area.strip()))
    normalized_labels = tuple(dict.fromkeys(label.strip() for label in labels if label.strip()))
    return tuple(f'{area} label:"{label}" state:open' for area in normalized_areas for label in normalized_labels)
