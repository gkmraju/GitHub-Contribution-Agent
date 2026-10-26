import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from github_contribution_agent.audit import (
    AuditEvent,
    AuditValidation,
    append_audit_event,
)


def event(**overrides):
    values = {
        "event_id": "evt-1",
        "run_id": "run-1",
        "occurred_at": "2026-10-06T10:00:00Z",
        "event_type": "validation",
        "repository": "owner/project",
        "decision": "draft_ready",
        "source_urls": ("https://github.com/owner/project/issues/3",),
        "issue_url": "https://github.com/owner/project/issues/3",
        "branch": "fix/issue-3",
        "commit": "a" * 40,
        "changed_paths": ("src/fix.py",),
        "validations": (AuditValidation("python -m unittest", "passed", 0),),
        "human_actions": ("Review the draft PR",),
    }
    values.update(overrides)
    return AuditEvent(**values)


class AuditLogTests(unittest.TestCase):
    def test_appends_one_json_line_without_command_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "runtime" / "events.jsonl"

            append_audit_event(path, event())

            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            recorded = json.loads(lines[0])
            self.assertEqual(recorded["validations"][0]["state"], "passed")
            self.assertNotIn("output", recorded)

    def test_appends_without_replacing_prior_events(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"

            append_audit_event(path, event())
            append_audit_event(path, event(event_id="evt-2", decision="reviewed"))

            self.assertEqual(len(path.read_text(encoding="utf-8").splitlines()), 2)

    def test_rejects_timezone_free_timestamps(self):
        with self.assertRaisesRegex(ValueError, "include a timezone"):
            event(occurred_at="2026-10-06T10:00:00").to_json_line()

    def test_rejects_secret_like_values(self):
        with self.assertRaisesRegex(ValueError, "must not contain credentials"):
            event(human_actions=("token ghp_" + "A" * 30,)).to_json_line()

    def test_rejects_sensitive_query_parameters(self):
        with self.assertRaisesRegex(ValueError, "credential query"):
            event(source_urls=("https://github.com/owner/project?token=secret",)).to_json_line()

    def test_rejects_validation_state_that_overclaims(self):
        with self.assertRaisesRegex(ValueError, "exit_code 0"):
            event(validations=(AuditValidation("python -m unittest", "passed", 1),)).to_json_line()

    def test_rejects_parent_traversal_paths(self):
        with self.assertRaisesRegex(ValueError, "repository-relative"):
            event(changed_paths=("../secret.txt",)).to_json_line()


if __name__ == "__main__":
    unittest.main()
