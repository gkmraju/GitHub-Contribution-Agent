"""Core immutable records shared by the contribution workflow."""

from dataclasses import dataclass
from enum import Enum


class Route(str, Enum):
    """Permitted result of evaluating an opportunity."""

    UPSTREAM = "upstream"
    FALLBACK = "fallback"
    REJECT = "reject"


@dataclass(frozen=True, slots=True)
class Opportunity:
    """Evidence collected before deciding whether to contribute upstream."""

    repository: str
    issue_url: str
    title: str
    area: str
    state: str = "open"
    contribution_guide_reviewed: bool = False
    discussion_reviewed: bool = False
    conventions_reviewed: bool = False
    relevant_files_reviewed: bool = False
    tests_identified: bool = False
    scope_clear: bool = False
    active_duplicate: bool = False
    low_value: bool = False
    speculative: bool = False
    authorized_write_path: bool = False
    requires_legal_attestation: bool = False
    requires_personal_representation: bool = False


@dataclass(frozen=True, slots=True)
class Decision:
    """Auditable route plus the reasons that produced it."""

    route: Route
    reasons: tuple[str, ...]
