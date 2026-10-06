import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from github_contribution_agent.execution.draft_pr import (
    DraftPullRequestInput,
    ValidationEvidence,
    ValidationState,
    prepare_draft_pull_request,
)


def request(**overrides):
    values = {
        "repository": "owner/project",
        "issue_url": "https://github.com/owner/project/issues/12",
        "base_branch": "main",
        "head_branch": "fix/issue-12",
        "title": "fix(parser): preserve the default encoding",
        "summary": "Preserve the documented encoding when parsing a one-item response.",
        "changed_files": ("src/parser.py", "tests/test_parser.py"),
        "validation": (
            ValidationEvidence("python -m unittest", ValidationState.PASSED),
            ValidationEvidence("ruff check src", ValidationState.NOT_RUN),
        ),
    }
    values.update(overrides)
    return DraftPullRequestInput(**values)


class DraftPullRequestTests(unittest.TestCase):
    def test_generates_draft_with_observed_validation_states(self):
        draft = prepare_draft_pull_request(request())

        self.assertTrue(draft.draft)
        self.assertIn("python -m unittest", draft.body)
        self.assertIn("passed", draft.body)
        self.assertIn("ruff check src", draft.body)
        self.assertIn("not run", draft.body)
        self.assertIn("Review the diff and CI", draft.body)

    def test_records_no_validation_as_not_run(self):
        draft = prepare_draft_pull_request(request(validation=()))

        self.assertIn("validation was not run", draft.body)

    def test_requires_unique_changed_files(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            prepare_draft_pull_request(
                request(changed_files=("src/parser.py", "src/parser.py"))
            )

    def test_rejects_parent_paths(self):
        with self.assertRaisesRegex(ValueError, "repository-relative"):
            prepare_draft_pull_request(request(changed_files=("../secrets",)))

    def test_rejects_same_base_and_head(self):
        with self.assertRaisesRegex(ValueError, "differ"):
            prepare_draft_pull_request(
                request(base_branch="main", head_branch="main")
            )

    def test_requires_title_on_one_line(self):
        with self.assertRaisesRegex(ValueError, "one line"):
            prepare_draft_pull_request(request(title="bad\ntitle"))

    def test_does_not_claim_pr_was_opened(self):
        draft = prepare_draft_pull_request(request())

        self.assertNotIn("opened successfully", draft.body.casefold())
        self.assertNotIn("ready for review", draft.body.casefold())


if __name__ == "__main__":
    unittest.main()
