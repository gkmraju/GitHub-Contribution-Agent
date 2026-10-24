import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from github_contribution_agent.analysis.repo_health import (
    RepoSnapshot,
    audit_repositories,
    audit_repository,
    render_markdown,
)

AS_OF = datetime(2026, 8, 17, tzinfo=UTC)


def snapshot(name: str, **overrides) -> RepoSnapshot:
    values = {
        "owner": "example",
        "name": name,
        "html_url": f"https://github.com/example/{name}",
        "default_branch": "main",
        "pushed_at": datetime(2026, 8, 1, tzinfo=UTC),
        "files": (
            ".github/workflows/ci.yml",
            ".github/dependabot.yml",
            ".gitignore",
            "SECURITY.md",
            "CODEOWNERS",
            "LICENSE",
            "CONTRIBUTING.md",
            "README.md",
            "pyproject.toml",
            "src/project.py",
            "tests/test_project.py",
        ),
    }
    values.update(overrides)
    return RepoSnapshot(**values)


class RepositoryHealthTests(unittest.TestCase):
    def test_scores_active_well_instrumented_original_repository(self):
        audit = audit_repository(snapshot("healthy"), as_of=AS_OF)

        self.assertGreaterEqual(audit.overall_score, 90)
        self.assertFalse(audit.opportunities)

    def test_ranks_actionable_original_ahead_of_healthy_repository(self):
        neglected = snapshot(
            "neglected",
            pushed_at=datetime(2023, 1, 1, tzinfo=UTC),
            files=("app.py",),
        )

        audits = audit_repositories((snapshot("healthy"), neglected), as_of=AS_OF)

        self.assertEqual(audits[0].repository.name, "neglected")
        self.assertIn("CI workflow", audits[0].opportunities[0])

    def test_non_divergent_fork_only_gets_fork_lifecycle_recommendations(self):
        fork = snapshot(
            "fork",
            fork=True,
            upstream_full_name="upstream/project",
            upstream_ahead_by=3,
            upstream_behind_by=18,
            pushed_at=datetime(2023, 1, 1, tzinfo=UTC),
            files=("app.py",),
        )

        audit = audit_repository(fork, as_of=AS_OF)
        joined = " ".join(audit.opportunities).casefold()

        self.assertIn("sync or assess", joined)
        self.assertIn("ahead commits", joined)
        self.assertIn("archive", joined)
        self.assertNotIn("tests", joined)
        self.assertNotIn("ci workflow", joined)

    def test_purposeful_fork_divergence_can_receive_engineering_opportunities(self):
        fork = snapshot(
            "product-fork",
            fork=True,
            purposeful_divergence=True,
            files=("app.py", "README.md"),
        )

        audit = audit_repository(fork, as_of=AS_OF)

        self.assertTrue(any("CI workflow" in item for item in audit.opportunities))
        self.assertTrue(
            any("deterministic tests" in item for item in audit.opportunities)
        )

    def test_docs_only_profile_does_not_get_code_tooling_recommendations(self):
        profile = snapshot("example", files=("README.md",))

        audit = audit_repository(profile, as_of=AS_OF)
        joined = " ".join(audit.opportunities).casefold()

        self.assertEqual(audit.scores.ci, 100)
        self.assertEqual(audit.scores.tests, 100)
        self.assertNotIn("ci workflow", joined)
        self.assertNotIn("tests", joined)

    def test_archived_repository_has_no_optimization_priority(self):
        audit = audit_repository(snapshot("archive", archived=True), as_of=AS_OF)

        self.assertEqual(audit.priority, 0)
        self.assertIn("read-only", audit.opportunities[0])

    def test_markdown_report_contains_rank_and_top_opportunity(self):
        audits = audit_repositories(
            (snapshot("healthy"), snapshot("needs-docs", files=("app.py",))),
            as_of=AS_OF,
        )

        report = render_markdown(audits, owner="example")

        self.assertIn("# Repository health audit: example", report)
        self.assertIn("| Rank | Repository |", report)
        self.assertIn("example/needs-docs", report)


if __name__ == "__main__":
    unittest.main()
