import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from github_contribution_agent.execution.codex import (
    CodexExecutionRequest,
    create_codex_execution_session,
    validate_execution_request,
)


def request(**overrides):
    values = {
        "task": "Fix the parsing bug with a focused regression test.",
        "repository": "owner/project",
        "issue_url": "https://github.com/owner/project/issues/4",
        "workspace_directory": "/tmp/project-worktree",
        "branch_name": "fix/parser-edge-case",
        "default_branch": "main",
        "base_revision": "a" * 40,
        "allowed_paths": ("src/parser.py", "tests/test_parser.py"),
        "validation_commands": ("python -m unittest tests.test_parser",),
        "model": "gpt-6-astra",
        "human_approved": True,
        "workspace_isolated": True,
    }
    values.update(overrides)
    return CodexExecutionRequest(**values)


class FakeSessions:
    def __init__(self):
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(
            id="sess_example",
            environment=SimpleNamespace(
                id="env_example",
                remote_url="https://api.openai.com/v1/agents/api",
            ),
        )


class CodexExecutionAdapterTests(unittest.TestCase):
    def test_rejects_request_without_human_approval(self):
        with self.assertRaisesRegex(ValueError, "human must approve"):
            validate_execution_request(request(human_approved=False))

    def test_rejects_non_isolated_workspace(self):
        with self.assertRaisesRegex(ValueError, "isolated workspace"):
            validate_execution_request(request(workspace_isolated=False))

    def test_rejects_repository_default_branch(self):
        with self.assertRaisesRegex(ValueError, "non-default branch"):
            validate_execution_request(request(branch_name="main"))

    def test_rejects_custom_repository_default_branch(self):
        with self.assertRaisesRegex(ValueError, "non-default branch"):
            validate_execution_request(
                request(branch_name="stable", default_branch="stable")
            )

    def test_rejects_parent_traversal_path(self):
        with self.assertRaisesRegex(ValueError, "must not escape"):
            validate_execution_request(request(allowed_paths=("../secrets.txt",)))

    def test_rejects_publication_authorization(self):
        with self.assertRaisesRegex(ValueError, "cannot publish"):
            validate_execution_request(request(publication_authorized=True))

    def test_creates_a_scoped_self_hosted_session(self):
        sessions = FakeSessions()
        client = SimpleNamespace(beta=SimpleNamespace(agents=SimpleNamespace(
            sessions=sessions
        )))

        session = create_codex_execution_session(request(), client=client)

        self.assertEqual(session.session_id, "sess_example")
        self.assertEqual(session.environment_id, "env_example")
        self.assertEqual(
            sessions.kwargs["environment"],
            {"type": "self_hosted", "workspace_directory": "/tmp/project-worktree"},
        )
        self.assertIn("Do not switch branches", sessions.kwargs["agent"]["instructions"])
        self.assertIn("Do not publish the work", sessions.kwargs["input"])
        self.assertNotIn("CODEX_API_KEY", str(sessions.kwargs))
        self.assertNotIn("OPENAI_API_KEY", str(sessions.kwargs))


if __name__ == "__main__":
    unittest.main()
