"""Deterministic safety gate for candidate contribution opportunities."""

from github_contribution_agent.models import Decision, Opportunity, Route


def assess_opportunity(opportunity: Opportunity) -> Decision:
    """Classify an opportunity without performing any GitHub write.

    Unsafe or wasteful work is rejected. A legitimate opportunity with incomplete
    evidence or no authorized write path is routed to the fallback workspace.
    """

    rejection_reasons: list[str] = []
    if opportunity.state.casefold() != "open":
        rejection_reasons.append("issue is not open")
    if opportunity.active_duplicate:
        rejection_reasons.append("an active or completed duplicate change exists")
    if opportunity.low_value:
        rejection_reasons.append("change is low value")
    if opportunity.speculative:
        rejection_reasons.append("change is speculative")
    if opportunity.requires_legal_attestation:
        rejection_reasons.append("contribution requires a legal attestation")
    if opportunity.requires_personal_representation:
        rejection_reasons.append("contribution requires a personal representation")

    if rejection_reasons:
        return Decision(Route.REJECT, tuple(rejection_reasons))

    evidence = {
        "contribution guide was not reviewed": opportunity.contribution_guide_reviewed,
        "issue discussion was not reviewed": opportunity.discussion_reviewed,
        "repository conventions were not reviewed": opportunity.conventions_reviewed,
        "relevant files were not reviewed": opportunity.relevant_files_reviewed,
        "relevant tests were not identified": opportunity.tests_identified,
        "scope is not clear": opportunity.scope_clear,
    }
    fallback_reasons = [reason for reason, present in evidence.items() if not present]
    if not opportunity.authorized_write_path:
        fallback_reasons.append("no authorized fork or upstream write path is available")

    if fallback_reasons:
        return Decision(Route.FALLBACK, tuple(fallback_reasons))

    return Decision(Route.UPSTREAM, ("evidence and authorized write path are complete",))
