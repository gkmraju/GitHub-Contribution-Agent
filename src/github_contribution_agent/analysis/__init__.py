from .duplicates import (
    DuplicateCandidate,
    DuplicateReport,
    IssueRecord,
    find_duplicate_candidates,
    issue_identity_from_url,
)
from .gate import assess_opportunity

__all__ = [
    "DuplicateCandidate",
    "DuplicateReport",
    "IssueRecord",
    "assess_opportunity",
    "find_duplicate_candidates",
    "issue_identity_from_url",
]
