"""Summarize process metrics from structured JSONL audit events."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def summarize_audit_log(path: str | Path) -> dict[str, Any]:
    """Count recorded events, unique runs, decisions, and validation outcomes."""
    event_types: Counter[str] = Counter()
    decisions: Counter[str] = Counter()
    validations: Counter[str] = Counter()
    run_ids: set[str] = set()
    total = 0

    with Path(path).open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSON on line {line_number}") from error
            if not isinstance(event, dict):
                raise ValueError(f"event on line {line_number} must be an object")
            run_id = event.get("run_id")
            event_type = event.get("event_type")
            decision = event.get("decision")
            if not all(isinstance(value, str) and value for value in (run_id, event_type, decision)):
                raise ValueError(f"event on line {line_number} lacks required string fields")
            run_ids.add(run_id)
            event_types[event_type] += 1
            decisions[decision] += 1
            records = event.get("validations", [])
            if not isinstance(records, list):
                raise ValueError(f"validations on line {line_number} must be a list")
            for validation in records:
                if not isinstance(validation, dict) or validation.get("state") not in {
                    "passed", "failed", "not_run"
                }:
                    raise ValueError(f"invalid validation record on line {line_number}")
                validations[validation["state"]] += 1
            total += 1

    return {
        "events": total,
        "unique_runs": len(run_ids),
        "events_by_type": dict(sorted(event_types.items())),
        "decisions": dict(sorted(decisions.items())),
        "validations": dict(sorted(validations.items())),
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python -m github_contribution_agent.metrics AUDIT.jsonl", file=sys.stderr)
        return 2
    try:
        print(json.dumps(summarize_audit_log(sys.argv[1]), indent=2, sort_keys=True))
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
