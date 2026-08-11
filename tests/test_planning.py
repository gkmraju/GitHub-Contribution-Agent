import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from github_contribution_agent.planning import FallbackTask, select_fallback


class SelectFallbackTests(unittest.TestCase):
    def test_selects_highest_value_reviewable_validated_task(self):
        tasks = (
            FallbackTask("speculative-large-change", 100, False, "python -m unittest"),
            FallbackTask("document-rules", 20, True, "python -m unittest"),
            FallbackTask("add-safety-gate", 80, True, "python -m unittest"),
        )

        self.assertEqual(select_fallback(tasks).slug, "add-safety-gate")

    def test_rejects_tasks_without_reviewable_validation(self):
        with self.assertRaises(ValueError):
            select_fallback((FallbackTask("activity-only", 10, False, ""),))


if __name__ == "__main__":
    unittest.main()
