"""Conservative duplicate screening for researched GitHub issues.

The matcher produces review candidates only. It never closes an issue, rejects a
contribution, or treats text similarity as proof that two reports are duplicates.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlsplit


_STOP_WORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from",
        "have", "how", "i", "if", "in", "is", "it", "of", "on", "or", "that",
        "the", "this", "to", "was", "when", "with", "would", "you",
    }
)
_TOKEN = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True, slots=True)
class IssueRecord:
    """Minimal, source-linked issue snapshot used for duplicate screening."""

    repository: str
    number: int
    title: str
    url: str
    body: str = ""
    state: str = "open"
    is_pull_request: bool = False


@dataclass(frozen=True, slots=True)
class DuplicateCandidate:
    """A same-repository issue that should be inspected by a human."""

    issue: IssueRecord
    title_similarity: int
    body_similarity: int
    combined_similarity: int
    confidence: str


@dataclass(frozen=True, slots=True)
class DuplicateReport:
    """Exact identity matches and ranked text-similarity candidates."""

    exact_matches: tuple[IssueRecord, ...]
    candidates: tuple[DuplicateCandidate, ...]
    compared_count: int


def find_duplicate_candidates(
    target: IssueRecord,
    issues: tuple[IssueRecord, ...] | list[IssueRecord],
    *,
    threshold: int = 55,
) -> DuplicateReport:
    """Return exact references and likely text matches for human review.

    Exact identity is based on case-insensitive repository plus issue number.
    Fuzzy comparisons are limited to the same repository because matching issue
    text across unrelated projects is not sufficient evidence of duplicate work.
    Pull requests are excluded; callers should search issues and PRs separately.
    """

    if not 0 <= threshold <= 100:
        raise ValueError("threshold must be between 0 and 100")

    target_repo = _normalize_repository(target.repository)
    exact: list[IssueRecord] = []
    ranked: list[DuplicateCandidate] = []
    compared = 0

    for issue in issues:
        if issue.is_pull_request:
            continue
        if _normalize_repository(issue.repository) != target_repo:
            continue
        if issue.number == target.number:
            exact.append(issue)
            continue

        compared += 1
        title_score = _similarity(target.title, issue.title)
        body_score = _similarity(target.body, issue.body)
        combined = (
            round(title_score * 0.7 + body_score * 0.3)
            if target.body.strip() and issue.body.strip()
            else title_score
        )
        if combined < threshold:
            continue
        ranked.append(
            DuplicateCandidate(
                issue=issue,
                title_similarity=title_score,
                body_similarity=body_score,
                combined_similarity=combined,
                confidence="likely" if combined >= 80 else "possible",
            )
        )

    ranked.sort(key=lambda item: (-item.combined_similarity, item.issue.number))
    exact.sort(key=lambda item: item.number)
    return DuplicateReport(tuple(exact), tuple(ranked), compared)


def issue_identity_from_url(url: str) -> tuple[str, str, int] | None:
    """Parse a canonical github.com issue URL into host, repository, and number."""

    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or parsed.netloc.casefold() != "github.com":
        return None
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 4 or parts[2] != "issues" or not parts[3].isdigit():
        return None
    return ("github.com", f"{parts[0]}/{parts[1]}".casefold(), int(parts[3]))


def _normalize_repository(repository: str) -> str:
    return repository.strip().strip("/").casefold()


def _similarity(left: str, right: str) -> int:
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens or not right_tokens:
        return 0
    union = left_tokens | right_tokens
    return round(100 * len(left_tokens & right_tokens) / len(union))


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in _TOKEN.findall(value.casefold())
        if len(token) > 1 and token not in _STOP_WORDS
    }
