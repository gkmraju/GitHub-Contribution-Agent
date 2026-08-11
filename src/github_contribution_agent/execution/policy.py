"""Publication safeguards that prevent unsupported or personal claims."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PublicationEvidence:
    validation_commands: tuple[str, ...] = ()
    successful_commands: tuple[str, ...] = ()
    claims_tests_passed: bool = False
    pull_request_is_draft: bool = True
    accepts_legal_attestation: bool = False
    makes_personal_representation: bool = False


def validate_publication(evidence: PublicationEvidence) -> tuple[str, ...]:
    """Return policy violations; an empty tuple means publication is allowed."""

    violations: list[str] = []
    if evidence.claims_tests_passed:
        if not evidence.validation_commands:
            violations.append("tests are claimed as passed without recorded commands")
        missing = set(evidence.validation_commands) - set(evidence.successful_commands)
        if missing:
            violations.append("not every claimed validation command completed successfully")
    if not evidence.pull_request_is_draft:
        violations.append("pull request must be opened as a draft")
    if evidence.accepts_legal_attestation:
        violations.append("legal attestations cannot be accepted")
    if evidence.makes_personal_representation:
        violations.append("personal representations cannot be made")
    return tuple(violations)
