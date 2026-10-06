"""Generate a fact-grounded draft pull request without publishing it."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import PurePosixPath
import re


class ValidationState(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    NOT_RUN = "not_run"


@dataclass(frozen=True, slots=True)
class ValidationEvidence:
    command: str
    state: ValidationState
    details: str = ""


@dataclass(frozen=True, slots=True)
class DraftPullRequestInput:
    repository: str
    issue_url: str
    base_branch: str
    head_branch: str
    title: str
    summary: str
    changed_files: tuple[str, ...]
    validation: tuple[ValidationEvidence, ...]
    risks: tuple[str, ...] = ()
    human_followups: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DraftPullRequest:
    """A ready-to-review body; no GitHub request has been made."""

    title: str
    body: str
    draft: bool = True


def prepare_draft_pull_request(request: DraftPullRequestInput) -> DraftPullRequest:
    """Render a draft PR body from recorded facts and observed validation results."""

    required = {
        "repository": request.repository,
        "issue_url": request.issue_url,
        "base_branch": request.base_branch,
        "head_branch": request.head_branch,
        "title": request.title,
        "summary": request.summary,
    }
    missing = [name for name, value in required.items() if not value.strip()]
    if missing:
        raise ValueError(f"required fields are empty: {', '.join(missing)}")
    if request.base_branch == request.head_branch:
        raise ValueError("head branch must differ from the base branch")
    if "\n" in request.title or "\r" in request.title or len(request.title) > 256:
        raise ValueError("title must be one line and no longer than 256 characters")
    if not request.changed_files:
        raise ValueError("at least one changed file must be recorded")
    _validate_file_paths(request.changed_files)
    if any(not item.command.strip() for item in request.validation):
        raise ValueError("validation commands must not be empty")

    lines = [
        f"Resolves {request.issue_url}",
        "",
        "## Summary",
        "",
        request.summary.strip(),
        "",
        "## Changed files",
        "",
    ]
    lines.extend(f"- `{_escape_inline(path)}`" for path in request.changed_files)
    lines.extend(["", "## Validation", ""])
    if request.validation:
        for item in request.validation:
            state = item.state.value
            line = f"- `{_escape_inline(item.command)}` — {state.replace('_', ' ')}"
            if item.details.strip():
                line += f": {_escape_inline(item.details.strip())}"
            lines.append(line)
    else:
        lines.append("- No validation command was recorded; validation was not run.")

    lines.extend(["", "## Risks and limitations", ""])
    lines.extend(f"- {risk.strip()}" for risk in request.risks if risk.strip())
    if not any(risk.strip() for risk in request.risks):
        lines.append("- None recorded.")

    lines.extend(["", "## Human follow-up", ""])
    lines.extend(f"- {item.strip()}" for item in request.human_followups if item.strip())
    if not any(item.strip() for item in request.human_followups):
        lines.append("- Review the diff and CI before marking this draft ready.")

    return DraftPullRequest(request.title.strip(), "\n".join(lines) + "\n")


def _validate_file_paths(paths: tuple[str, ...]) -> None:
    if len(paths) != len(set(paths)):
        raise ValueError("changed file paths must be unique")
    for value in paths:
        path = PurePosixPath(value)
        if (
            not value
            or "\\" in value
            or path.is_absolute()
            or any(part in {"", ".", ".."} for part in value.split("/"))
        ):
            raise ValueError("changed file paths must be repository-relative")


def _escape_inline(value: str) -> str:
    clean = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", value)
    return clean.replace("`", "\\`").replace("\n", " ").replace("\r", " ")
