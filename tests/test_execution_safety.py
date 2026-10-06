import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from github_contribution_agent.execution.safety import ExecutionRequest, validate_execution_request


def request(**changes):
    values = {
        "repository": "owner/project",
        "expected_repository": "owner/project",
        "base_ref": "agent/fix",
        "base_sha": "abc123",
        "changed_paths": ("src/package.py",),
        "allowed_paths": ("src", "tests"),
        "approved_by_maintainer": True,
    }
    values.update(changes)
    return ExecutionRequest(**values)


class ExecutionSafetyTests(unittest.TestCase):
    def test_accepts_approved_scoped_feature_branch(self):
        self.assertEqual(validate_execution_request(request()), ())

    def test_requires_explicit_approval(self):
        self.assertIn("explicit maintainer approval is required", validate_execution_request(
            request(approved_by_maintainer=False)
        ))

    def test_rejects_wrong_repository_and_default_branch(self):
        violations = validate_execution_request(request(
            repository="attacker/project", base_ref="main"
        ))
        self.assertIn("repository identity does not match the approved repository", violations)
        self.assertIn("execution must target a non-default feature branch", violations)

    def test_rejects_sensitive_or_out_of_scope_paths(self):
        violations = validate_execution_request(request(
            changed_paths=("src/.env.production", "docs/notes.md")
        ))
        self.assertTrue(any("sensitive path is blocked" in item for item in violations))
        self.assertTrue(any("outside the approved scope" in item for item in violations))

    def test_rejects_traversal_absolute_and_windows_paths(self):
        violations = validate_execution_request(request(
            changed_paths=("../outside.py", "/etc/passwd", "src\\outside.py")
        ))
        self.assertGreaterEqual(sum("relative and non-empty" in item for item in violations), 3)

    def test_enforces_file_limit_and_pinned_sha(self):
        violations = validate_execution_request(request(
            changed_paths=tuple(f"src/{i}.py" for i in range(11)), base_sha="", max_files=10
        ))
        self.assertIn("base commit SHA must be pinned", violations)
        self.assertIn("changed file count exceeds the approved limit", violations)


if __name__ == "__main__":
    unittest.main()
