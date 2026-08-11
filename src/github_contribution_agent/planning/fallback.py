"""Choose useful fallback work without optimizing for activity alone."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FallbackTask:
    slug: str
    value: int
    independently_reviewable: bool
    validation_command: str


def select_fallback(tasks: tuple[FallbackTask, ...]) -> FallbackTask:
    """Select the highest-value reviewable task with explicit validation."""

    eligible = [task for task in tasks if task.independently_reviewable and task.validation_command.strip()]
    if not eligible:
        raise ValueError("no independently reviewable fallback task with validation")
    return min(eligible, key=lambda task: (-task.value, task.slug))
