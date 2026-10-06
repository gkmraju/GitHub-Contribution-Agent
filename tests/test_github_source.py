import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from github_contribution_agent.scouting.github_source import (
    GitHubClient,
    collect_owned_repositories,
)


class FakeResponse:
    def __init__(self, value):
        self._buffer = io.BytesIO(json.dumps(value).encode("utf-8"))

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self._buffer.read()


class StubClient:
    def get_json(self, path, *, params=None):
        if path == "/users/example/repos":
            return [
                {
                    "name": "original",
                    "full_name": "example/original",
                    "html_url": "https://github.com/example/original",
                    "default_branch": "main",
                    "pushed_at": "2026-08-01T00:00:00Z",
                    "fork": False,
                    "archived": False,
                },
                {
                    "name": "fork",
                    "full_name": "example/fork",
                    "html_url": "https://github.com/example/fork",
                    "default_branch": "main",
                    "pushed_at": "2025-01-01T00:00:00Z",
                    "fork": True,
                    "archived": False,
                },
            ]
        if path.endswith("/git/trees/main"):
            return {"tree": [{"path": "README.md", "type": "blob"}], "truncated": False}
        if path == "/repos/example/fork":
            return {
                "parent": {"full_name": "upstream/project", "default_branch": "main"}
            }
        if path == "/repos/upstream/project/compare/main...example:main":
            return {"ahead_by": 2, "behind_by": 7}
        raise AssertionError((path, params))


class GitHubSourceTests(unittest.TestCase):
    @patch("github_contribution_agent.scouting.github_source.urlopen")
    def test_client_uses_authorization_header_without_putting_token_in_url(
        self, mocked
    ):
        mocked.return_value = FakeResponse({"ok": True})
        client = GitHubClient(token="secret-token")

        self.assertEqual(client.get_json("/rate_limit"), {"ok": True})

        request = mocked.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer secret-token")
        self.assertNotIn("secret-token", request.full_url)

    def test_collects_original_and_fork_divergence_snapshots(self):
        snapshots = collect_owned_repositories("example", client=StubClient())

        self.assertEqual([item.name for item in snapshots], ["original", "fork"])
        self.assertEqual(snapshots[0].files, ("README.md",))
        self.assertEqual(snapshots[1].upstream_full_name, "upstream/project")
        self.assertEqual(snapshots[1].upstream_ahead_by, 2)
        self.assertEqual(snapshots[1].upstream_behind_by, 7)


if __name__ == "__main__":
    unittest.main()
