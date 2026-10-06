import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from github_contribution_agent.analysis.duplicates import (
    IssueRecord,
    find_duplicate_candidates,
    issue_identity_from_url,
)


def issue(number, title, body="", **overrides):
    values = {
        "repository": "Example/Project",
        "number": number,
        "title": title,
        "url": f"https://github.com/example/project/issues/{number}",
        "body": body,
        "state": "open",
    }
    values.update(overrides)
    return IssueRecord(**values)


class DuplicateScreeningTests(unittest.TestCase):
    def test_reports_exact_issue_identity_separately(self):
        target = issue(7, "Original report")
        report = find_duplicate_candidates(target, [issue(7, "Changed title")])

        self.assertEqual(report.exact_matches[0].number, 7)
        self.assertEqual(report.candidates, ())
        self.assertEqual(report.compared_count, 0)

    def test_ranks_similar_same_repository_issue_for_human_review(self):
        target = issue(
            10,
            "Parser rejects a single version returned as a JSON array",
            "The installer fails when the registry responds with one version.",
        )
        candidate = issue(
            9,
            "Parser rejects a single version returned inside an array",
            "The installer fails when the registry responds with one version.",
        )

        report = find_duplicate_candidates(target, [candidate])

        self.assertEqual(report.candidates[0].issue.number, 9)
        self.assertEqual(report.candidates[0].confidence, "likely")
        self.assertGreaterEqual(report.candidates[0].combined_similarity, 80)

    def test_does_not_compare_across_repositories(self):
        target = issue(2, "Crash on startup")
        candidate = issue(1, "Crash on startup", repository="other/project")

        report = find_duplicate_candidates(target, [candidate])

        self.assertEqual(report.compared_count, 0)
        self.assertEqual(report.candidates, ())

    def test_excludes_pull_requests_from_issue_duplicate_candidates(self):
        target = issue(2, "Crash on startup")
        pull_request = issue(3, "Crash on startup", is_pull_request=True)

        report = find_duplicate_candidates(target, [pull_request])

        self.assertEqual(report.compared_count, 0)
        self.assertEqual(report.candidates, ())

    def test_empty_text_is_not_a_duplicate_signal(self):
        target = issue(2, "", "")
        candidate = issue(3, "", "")

        report = find_duplicate_candidates(target, [candidate])

        self.assertEqual(report.candidates, ())

    def test_rejects_invalid_threshold(self):
        with self.assertRaises(ValueError):
            find_duplicate_candidates(issue(1, "One"), [], threshold=101)

    def test_parses_only_canonical_issue_urls(self):
        self.assertEqual(
            issue_identity_from_url("https://github.com/Example/Project/issues/12"),
            ("github.com", "example/project", 12),
        )
        self.assertIsNone(issue_identity_from_url("https://github.com/Example/Project/pull/12"))
        self.assertIsNone(issue_identity_from_url("https://example.com/Example/Project/issues/12"))


if __name__ == "__main__":
    unittest.main()
