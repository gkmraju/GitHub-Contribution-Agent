import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from github_contribution_agent.analysis import assess_opportunity
from github_contribution_agent.models import Opportunity, Route


def researched_opportunity(**overrides):
    values = {
        "repository": "example/project",
        "issue_url": "https://github.com/example/project/issues/1",
        "title": "Confirmed serialization bug",
        "area": "artificial-intelligence",
        "contribution_guide_reviewed": True,
        "discussion_reviewed": True,
        "conventions_reviewed": True,
        "relevant_files_reviewed": True,
        "tests_identified": True,
        "scope_clear": True,
    }
    values.update(overrides)
    return Opportunity(**values)


class AssessOpportunityTests(unittest.TestCase):
    def test_routes_researched_issue_to_fallback_without_write_path(self):
        decision = assess_opportunity(researched_opportunity())

        self.assertEqual(decision.route, Route.FALLBACK)
        self.assertIn("no authorized fork or upstream write path is available", decision.reasons)

    def test_rejects_duplicate_work(self):
        decision = assess_opportunity(researched_opportunity(active_duplicate=True))

        self.assertEqual(decision.route, Route.REJECT)
        self.assertIn("duplicate", decision.reasons[0])

    def test_rejects_legal_attestation(self):
        decision = assess_opportunity(researched_opportunity(requires_legal_attestation=True))

        self.assertEqual(decision.route, Route.REJECT)

    def test_allows_small_upstream_change_when_evidence_and_path_are_complete(self):
        decision = assess_opportunity(researched_opportunity(authorized_write_path=True))

        self.assertEqual(decision.route, Route.UPSTREAM)

    def test_incomplete_research_uses_fallback(self):
        decision = assess_opportunity(researched_opportunity(tests_identified=False))

        self.assertEqual(decision.route, Route.FALLBACK)
        self.assertIn("relevant tests were not identified", decision.reasons)


if __name__ == "__main__":
    unittest.main()
