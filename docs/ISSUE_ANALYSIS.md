# Issue analysis and duplicate screening

`analysis.duplicates.find_duplicate_candidates` compares a researched issue with
issue records already collected by the caller. The function is deterministic and
offline; it performs no GitHub requests or writes.

## Example

```python
from github_contribution_agent.analysis import IssueRecord, find_duplicate_candidates

target = IssueRecord(
    repository="owner/project",
    number=42,
    title="Parser rejects a single version returned as an array",
    url="https://github.com/owner/project/issues/42",
    body="The installer fails when the registry returns one version in an array.",
)

report = find_duplicate_candidates(target, previously_researched_issues)

for issue in report.exact_matches:
    print("Same issue:", issue.url)
for candidate in report.candidates:
    print(candidate.confidence, candidate.combined_similarity, candidate.issue.url)
```

## How to interpret results

- Exact matches use the normalized repository name and issue number.
- Fuzzy matching is limited to issues in the same repository. Pull requests are
  excluded because issue and PR duplicate searches should remain separately
  inspectable.
- Text matching tokenizes title and body and computes Jaccard overlap. The title
  contributes 70% and the body 30% when both bodies are present; otherwise the
  title score is used.
- The default threshold is 55/100. Scores at or above 80 are labeled `likely`;
  lower matching scores are labeled `possible`.
- Candidates are sorted by score, then issue number. Closed issues remain eligible
  because they may already contain the fix or point to the canonical report.

A `likely` or `possible` match is a review prompt, not a duplicate verdict.
Inspect issue discussion, linked pull requests, current code, and fix status before
routing an opportunity. Similar wording can describe different failures, and
different wording can describe the same underlying bug. The matcher must never
auto-close issues or automatically reject contributions.
