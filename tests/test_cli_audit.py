import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from github_contribution_agent.cli import main


class AuditCLIIntegrationTests(unittest.TestCase):
    def test_renders_ranked_markdown_from_offline_snapshot(self):
        payload = [
            {
                "owner": "example",
                "name": "project",
                "html_url": "https://github.com/example/project",
                "default_branch": "main",
                "pushed_at": "2026-08-01T12:00:00Z",
                "files": ["README.md", "app.py"],
            }
        ]
        with TemporaryDirectory() as directory:
            snapshot = Path(directory) / "repositories.json"
            snapshot.write_text(json.dumps(payload), encoding="utf-8")
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                result = main(
                    [
                        "audit-repos",
                        "example",
                        "--input",
                        str(snapshot),
                        "--as-of",
                        "2026-08-17T18:30:00+00:00",
                    ]
                )

        self.assertEqual(result, 0)
        self.assertIn("# Repository health audit: example", stdout.getvalue())
        self.assertIn("add a minimal CI workflow", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
