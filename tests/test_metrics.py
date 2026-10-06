import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from github_contribution_agent.metrics import summarize_audit_log


class AuditMetricsTests(unittest.TestCase):
    def test_counts_events_runs_decisions_and_validation_states(self):
        events = [
            {"run_id": "r1", "event_type": "planned", "decision": "upstream",
             "validations": [{"state": "passed"}, {"state": "not_run"}]},
            {"run_id": "r1", "event_type": "validated", "decision": "upstream",
             "validations": [{"state": "failed"}]},
            {"run_id": "r2", "event_type": "stopped", "decision": "fallback",
             "validations": []},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            path.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
            self.assertEqual(summarize_audit_log(path), {
                "events": 3,
                "unique_runs": 2,
                "events_by_type": {"planned": 1, "stopped": 1, "validated": 1},
                "decisions": {"fallback": 1, "upstream": 2},
                "validations": {"failed": 1, "not_run": 1, "passed": 1},
            })

    def test_rejects_invalid_json_with_line_number(self):
        event = {"run_id": "r1", "event_type": "planned", "decision": "upstream"}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            path.write_text(json.dumps(event) + "\nnot-json\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 2"):
                summarize_audit_log(path)

    def test_rejects_invalid_validation_state(self):
        event = {"run_id": "r1", "event_type": "check", "decision": "upstream",
                 "validations": [{"state": "unknown"}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            path.write_text(json.dumps(event), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "validation record"):
                summarize_audit_log(path)


if __name__ == "__main__":
    unittest.main()
