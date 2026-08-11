import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from github_contribution_agent.scouting import build_issue_queries


class BuildQueriesTests(unittest.TestCase):
    def test_builds_stable_deduplicated_queries(self):
        queries = build_issue_queries(
            ("finance", "finance", "artificial-intelligence"),
            ("bug", "help wanted"),
        )

        self.assertEqual(
            queries,
            (
                'finance label:"bug" state:open',
                'finance label:"help wanted" state:open',
                'artificial-intelligence label:"bug" state:open',
                'artificial-intelligence label:"help wanted" state:open',
            ),
        )


if __name__ == "__main__":
    unittest.main()
