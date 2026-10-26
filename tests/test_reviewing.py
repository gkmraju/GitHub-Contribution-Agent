import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from github_contribution_agent.reviewing import (
    ReviewThread,
    prepare_review_response_plan,
)


class ReviewResponsePlannerTests(unittest.TestCase):
    def test_lists_only_unresolved_threads_for_human_action(self):
        plan = prepare_review_response_plan(
            "https://github.com/owner/project/pull/8",
            [
                ReviewThread("resolved", "Already addressed", True, "src/a.py", 4),
                ReviewThread("open", "Please add a regression test.", False, "tests/a.py", 12, "reviewer"),
            ],
        )

        self.assertEqual(plan.resolved_thread_count, 1)
        self.assertEqual(len(plan.actions), 1)
        self.assertTrue(plan.requires_human_action)
        self.assertIn("response not sent", plan.to_markdown())
        self.assertIn("Please add a regression test.", plan.to_markdown())

    def test_escapes_html_in_reviewer_content(self):
        plan = prepare_review_response_plan(
            "https://github.com/owner/project/pull/8",
            [ReviewThread("node-1", "<script>alert(1)</script>", False)],
        )

        self.assertIn("&lt;script&gt;", plan.to_markdown())
        self.assertNotIn("<script>", plan.to_markdown())

    def test_empty_plan_is_explicit(self):
        plan = prepare_review_response_plan(
            "https://github.com/owner/project/pull/8", []
        )

        self.assertFalse(plan.requires_human_action)
        self.assertIn("No unresolved", plan.to_markdown())

    def test_rejects_non_github_pull_request_url(self):
        with self.assertRaisesRegex(ValueError, "HTTPS GitHub URL"):
            prepare_review_response_plan("https://example.com/pr/1", [])

    def test_rejects_duplicate_thread_ids(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            prepare_review_response_plan(
                "https://github.com/owner/project/pull/8",
                [
                    ReviewThread("same", "One", False),
                    ReviewThread("same", "Two", False),
                ],
            )

    def test_rejects_unsafe_repository_path(self):
        with self.assertRaisesRegex(ValueError, "repository-relative"):
            prepare_review_response_plan(
                "https://github.com/owner/project/pull/8",
                [ReviewThread("one", "Comment", False, "../secret", 1)],
            )


if __name__ == "__main__":
    unittest.main()
