"""Bounded, evidence-aware plans for contribution opportunities."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PlanRoute(str, Enum):
    """What should happen next; planning never executes the selected work."""

    UPSTREAM = "upstream"
    FALLBACK = "fallback"
    RESEARCH = "research"
    REJECT = "reject"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class ContributionCandidate:
    """Facts gathered before planning a contribution."""

    repository: str
    issue_url: str
    title: str
    state: str = "open"
    value_score: int = 50
    evidence_complete: bool = False
    scope_clear: bool = False
    duplicate_status: str = "unreviewed"
    estimated_changed_files: int = 1
    validation_commands: tuple[str, ...] = ()
    authorized_write_path: bool = False
    fallback_available: bool = False
    requires_legal_attestation: bool = False
    requires_personal_representation: bool = False


@dataclass(frozen=True, slots=True)
class ContributionPlan:
    """An auditable next-step recommendation, not an execution record."""

    route: PlanRoute
    repository: str
    issue_url: str
    scope_limit_files: int
    proposed_validation: tuple[str, ...]
    reasons: tuple[str, ...]


def plan_contribution(
    candidate: ContributionCandidate,
    *,
    max_changed_files: int = 5,
    minimum_value: int = 35,
) -> ContributionPlan:
    """Recommend a bounded route without performing repository or GitHub writes."""

    if max_changed_files < 1:
        raise ValueError("max_changed_files must be at least 1")
    if not 0 <= minimum_value <= 100:
        raise ValueError("minimum_value must be between 0 and 100")
    if not 0 <= candidate.value_score <= 100:
        raise ValueError("value_score must be between 0 and 100")
    if candidate.estimated_changed_files < 0:
        raise ValueError("estimated_changed_files cannot be negative")
    if candidate.duplicate_status not in {"clear", "unreviewed", "possible", "likely", "exact"}:
        raise ValueError("duplicate_status must be clear, unreviewed, possible, likely, or exact")

    base = {
        "repository": candidate.repository,
        "issue_url": candidate.issue_url,
        "scope_limit_files": max_changed_files,
        "proposed_validation": candidate.validation_commands,
    }

    if candidate.requires_legal_attestation or candidate.requires_personal_representation:
        return ContributionPlan(
            route=PlanRoute.BLOCKED,
            **base,
            reasons=("human action is required for a legal or personal representation",),
        )
    if candidate.state.casefold() != "open":
        return ContributionPlan(
            route=PlanRoute.REJECT,
            **base,
            reasons=("issue is not open",),
        )
    if candidate.value_score < minimum_value:
        return ContributionPlan(
            route=PlanRoute.REJECT,
            **base,
            reasons=("expected contribution value is below the configured minimum",),
        )

    research_gaps: list[str] = []
    if not candidate.evidence_complete:
        research_gaps.append("required repository and issue evidence is incomplete")
    if not candidate.scope_clear:
        research_gaps.append("the smallest useful scope is not yet clear")
    if candidate.duplicate_status in {"possible", "likely", "unreviewed", "exact"}:
        research_gaps.append("duplicate candidates need review")
    if not candidate.validation_commands:
        research_gaps.append("no relevant validation command has been identified")
    if candidate.estimated_changed_files > max_changed_files:
        research_gaps.append("reduce the proposed change to fit the file limit")

    if research_gaps:
        return ContributionPlan(
            route=PlanRoute.RESEARCH,
            **base,
            reasons=tuple(research_gaps),
        )

    if candidate.authorized_write_path:
        return ContributionPlan(
            route=PlanRoute.UPSTREAM,
            **base,
            reasons=("evidence, scope, duplicate review, validation, and write path are ready",),
        )
    if candidate.fallback_available:
        return ContributionPlan(
            route=PlanRoute.FALLBACK,
            **base,
            reasons=("no authorized upstream write path is available; use the fallback workspace",),
        )
    return ContributionPlan(
        route=PlanRoute.BLOCKED,
        **base,
        reasons=("no authorized upstream path or suitable fallback task is available",),
    )
