"""Prepare human-owned response checklists for GitHub review threads."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import PurePosixPath


@dataclass(frozen=True, slots=True)
class ReviewThread:
    """Read-only snapshot of one GitHub inline review thread."""

    thread_id: str
    body: str
    resolved: bool
    path: str = ""
    line: int | None = None
    reviewer: str = ""


@dataclass(frozen=True, slots=True)
class ReviewAction:
    """One unresolved thread requiring a human decision."""

    thread_id: str
    reviewer: str
    path: str
    line: int | None
    comment: str
    next_step: str = "Inspect the concern, decide the code action, then draft a factual reply."


@dataclass(frozen=True, slots=True)
class ReviewResponsePlan:
    pull_request_url: str
    actions: tuple[ReviewAction, ...]
    resolved_thread_count: int

    @property
    def requires_human_action(self) -> bool:
        return bool(self.actions)

    def to_markdown(self) -> str:
        lines = [
            f"# Review response plan: {self.pull_request_url}",
            "",
            f"Resolved threads observed: {self.resolved_thread_count}",
            f"Unresolved threads requiring human action: {len(self.actions)}",
            "",
        ]
        if not self.actions:
            lines.append("No unresolved inline threads were present in this snapshot.")
            return "\n".join(lines) + "\n"

        for index, action in enumerate(self.actions, start=1):
            location = action.path or "general"
            if action.line is not None:
                location += f":{action.line}"
            lines.extend(
                [
                    f"## {index}. {location}",
                    "",
                    f"- Thread ID: `{_escape_inline(action.thread_id)}`",
                    f"- Reviewer: {_escape_inline(action.reviewer) or 'unspecified'}",
                    "- Status: unresolved; response not sent",
                    f"- Next step: {action.next_step}",
                    "",
                    "> " + "\n> ".join(_escape_quote(action.comment).splitlines()),
                    "",
                ]
            )
        return "\n".join(lines)


def prepare_review_response_plan(
    pull_request_url: str,
    threads: tuple[ReviewThread, ...] | list[ReviewThread],
) -> ReviewResponsePlan:
    """Create an inspectable checklist; do not reply or change GitHub state."""

    if not pull_request_url.startswith("https://github.com/"):
        raise ValueError("pull_request_url must be an HTTPS GitHub URL")
    resolved_count = 0
    actions: list[ReviewAction] = []
    seen: set[str] = set()
    for thread in threads:
        if not thread.thread_id.strip():
            raise ValueError("review thread ID must not be empty")
        if thread.thread_id in seen:
            raise ValueError("review thread IDs must be unique")
        seen.add(thread.thread_id)
        if thread.resolved:
            resolved_count += 1
            continue
        if not thread.body.strip():
            raise ValueError("unresolved review thread body must not be empty")
        if thread.path:
            path = PurePosixPath(thread.path)
            if path.is_absolute() or ".." in path.parts or "\\" in thread.path:
                raise ValueError("review file path must be repository-relative")
        if thread.line is not None and thread.line < 1:
            raise ValueError("review line must be a positive number")
        actions.append(
            ReviewAction(
                thread_id=thread.thread_id,
                reviewer=thread.reviewer.strip(),
                path=thread.path,
                line=thread.line,
                comment=thread.body.strip(),
            )
        )
    actions.sort(key=lambda item: (item.path.casefold(), item.line or 0, item.thread_id))
    return ReviewResponsePlan(pull_request_url, tuple(actions), resolved_count)


def _escape_inline(value: str) -> str:
    return escape(value, quote=True).replace("`", "\\`").replace("\n", " ").replace("\r", " ")


def _escape_quote(value: str) -> str:
    return escape(value, quote=False).replace("\r", "")
