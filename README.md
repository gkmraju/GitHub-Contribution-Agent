# GitHub Contribution Agent

A responsible daily workflow for finding and completing small, useful open-source
contributions. The project separates research, analysis, planning, execution, and
fallback work so that activity never becomes the goal by itself.

## Principles

- Research current opportunities across AI, finance, open source, and software
  engineering.
- Read the contribution guide, issue discussion, relevant code, conventions, and
  tests before proposing a change.
- Reject duplicate, low-value, speculative, or oversized pull requests.
- Prefer the smallest change that solves a confirmed problem.
- Use the fallback workspace when an upstream contribution cannot be completed
  responsibly or through an authorized fork/write path.
- Never claim a validation passed unless that exact validation was run successfully.
- Never accept a CLA, DCO, legal attestation, or make a personal representation.
- Open pull requests as drafts until a human decides they are ready.

## Project layout

| Path | Responsibility |
| --- | --- |
| `src/github_contribution_agent/scouting/` | Discover and normalize opportunities |
| `src/github_contribution_agent/analysis/` | Apply evidence and safety gates |
| `src/github_contribution_agent/planning/` | Select the smallest useful next step |
| `src/github_contribution_agent/execution/` | Guard publication and validation claims |
| `fallback-contributions/` | Independently reviewable work when upstream is blocked |
| `logs/` | Daily evidence and decisions |
| `config/` | Topics, effort limits, and safety defaults |
| `tests/` | Deterministic offline tests |
| `.github/workflows/` | Continuous validation |

`quant-github-scout` remains a separate quant-repository discovery project. It may
be used as one future data source, but this repository owns contribution decisions,
execution safeguards, and fallback work.

## Run the validation

```console
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

The initial implementation uses only the Python standard library and supports
Python 3.11 or newer.

## Evaluate an opportunity

Create a JSON document matching the fields in `Opportunity`, then run:

```console
PYTHONPATH=src python -m github_contribution_agent evaluate opportunity.json
```

The result is `upstream`, `fallback`, or `reject`, with explicit reasons suitable
for a daily log.
