"""Small offline CLI for evaluating previously researched opportunities."""

import argparse
import json
from pathlib import Path

from github_contribution_agent.analysis import assess_opportunity
from github_contribution_agent.models import Opportunity


def evaluate_file(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    decision = assess_opportunity(Opportunity(**data))
    return {"route": decision.route.value, "reasons": list(decision.reasons)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="github-contribution-agent")
    subparsers = parser.add_subparsers(dest="command", required=True)
    evaluate = subparsers.add_parser("evaluate", help="evaluate a researched opportunity JSON file")
    evaluate.add_argument("path", type=Path)
    args = parser.parse_args(argv)

    if args.command == "evaluate":
        print(json.dumps(evaluate_file(args.path), indent=2, sort_keys=True))
    return 0
