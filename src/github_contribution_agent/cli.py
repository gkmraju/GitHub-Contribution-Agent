"""Small offline CLI for evaluating previously researched opportunities."""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from github_contribution_agent.analysis import (
    RepoSnapshot,
    assess_opportunity,
    audit_repositories,
    render_json,
    render_markdown,
)
from github_contribution_agent.models import Opportunity
from github_contribution_agent.scouting import collect_owned_repositories


def evaluate_file(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    decision = assess_opportunity(Opportunity(**data))
    return {"route": decision.route.value, "reasons": list(decision.reasons)}


def load_snapshots(path: Path) -> tuple[RepoSnapshot, ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    repositories = data.get("repositories", data) if isinstance(data, dict) else data
    if not isinstance(repositories, list):
        raise ValueError("snapshot input must be a list or contain a repositories list")
    return tuple(RepoSnapshot.from_mapping(item) for item in repositories)


def _as_of(value: str | None) -> datetime:
    if value is None:
        return datetime.now(UTC)
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="github-contribution-agent")
    subparsers = parser.add_subparsers(dest="command", required=True)
    evaluate = subparsers.add_parser(
        "evaluate", help="evaluate a researched opportunity JSON file"
    )
    evaluate.add_argument("path", type=Path)
    audit = subparsers.add_parser(
        "audit-repos",
        help="rank health and optimization opportunities across an owner's repositories",
    )
    audit.add_argument("owner")
    audit.add_argument(
        "--input",
        type=Path,
        help="use a saved repository snapshot instead of the live read-only GitHub API",
    )
    audit.add_argument(
        "--as-of", help="ISO date or timestamp for deterministic staleness scoring"
    )
    audit.add_argument("--format", choices=("json", "markdown"), default="markdown")
    audit.add_argument("--output", type=Path, help="write the report to a file")
    args = parser.parse_args(argv)

    if args.command == "evaluate":
        print(json.dumps(evaluate_file(args.path), indent=2, sort_keys=True))
        return 0

    if args.command == "audit-repos":
        repositories = (
            load_snapshots(args.input)
            if args.input
            else collect_owned_repositories(args.owner)
        )
        audits = audit_repositories(repositories, as_of=_as_of(args.as_of))
        report = (
            render_json(audits)
            if args.format == "json"
            else render_markdown(audits, owner=args.owner)
        )
        if args.output:
            args.output.write_text(report, encoding="utf-8")
        else:
            print(report, end="")
    return 0
