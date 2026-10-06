import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from github_contribution_agent.planning import (
    ContributionCandidate,
    PlanRoute,
    plan_contribution,
)


def candidate(**overrides):
    values = {
        "repository": "owner/project",
        "issue_url": "https://github.com/owner/project/issues/8",
        "title": "Fix a focused bug",
        "state": "open",
        "value_score": 70,
        "evidence_complete": True,
        "scope_clear": True,
        "duplicate_status": "clear",
        "estimated_changed_files": 2,
        "validation_commands": ("python -m unittest",),
        "authorized_write_path": True,
    }
    values.update(overrides)
    return ContributionCandidate(**values)


class ContributionPlanningTests(unittest.TestCase):
    def test_plans_upstream_only_when_gates_are_complete(self):
        plan = plan_contribution(candidate())

        self.assertEqual(plan.route, PlanRoute.UPSTREAM)
        self.assertEqual(plan.proposed_validation, ("python -m unittest",))

    def test_missing_evidence_routes_to_research(self):
        plan = plan_contribution(candidate(evidence_complete=False))

        self.assertEqual(plan.route, PlanRoute.RESEARCH)
        self.assertIn("evidence is incomplete", " ".join(plan.reasons))

    def test_duplicate_candidate_requires_review(self):
        plan = plan_contribution(candidate(duplicate_status="possible"))

        self.assertEqual(plan.route, PlanRoute.RESEARCH)
        self.assertIn("duplicate candidates need review", plan.reasons)

    def test_oversized_scope_returns_to_planning(self):
        plan = plan_contribution(candidate(estimated_changed_files=6))

        self.assertEqual(plan.route, PlanRoute.RESEARCH)
        self.assertIn("reduce the proposed change to fit the file limit", plan.reasons)

    def test_unauthorized_upstream_path_uses_available_fallback(self):
        plan = plan_contribution(
            candidate(authorized_write_path=False, fallback_available=True)
        )

        self.assertEqual(plan.route, PlanRoute.FALLBACK)

    def test_closed_issue_is_rejected(self):
        plan = plan_contribution(candidate(state="closed"))

        self.assertEqual(plan.route, PlanRoute.REJECT)

    def test_legal_attestation_requires_human_action(self):
        plan = plan_contribution(candidate(requires_legal_attestation=True))

        self.assertEqual(plan.route, PlanRoute.BLOCKED)

    def test_invalid_file_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            plan_contribution(candidate(), max_changed_files=0)


if __name__ == "__main__":
    unittest.main()
