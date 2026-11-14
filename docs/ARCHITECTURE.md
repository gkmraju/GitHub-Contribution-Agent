# Maintainer-agent architecture

## Purpose

The system should help a maintainer move from an open-source opportunity to a
small, reviewable, well-evidenced contribution. It must preserve human control of
publication, legal commitments, and consequential repository actions.

## Current implementation

The current Python package already separates several responsibilities:

| Area | Current responsibility |
| --- | --- |
| `scouting/` | Discover and normalize candidate opportunities |
| `analysis/` | Apply evidence, duplicate, value, and safety gates |
| `planning/` | Select a bounded next task |
| `execution/` | Check publication claims and safety policy |
| `fallback-contributions/` | Hold independently reviewable work when upstream work is blocked |
| `logs/` | Record dated research decisions and outcomes |
| `config/` | Store topics, effort limits, and safety defaults |
| `tests/` | Exercise deterministic offline behavior |
| `.github/workflows/` | Run repository validation |

The present CLI evaluates a previously researched opportunity. The analysis gate
does not write to GitHub. The publication policy checks recorded validation
claims, draft status, and prohibited attestations. These are foundations; they do
not yet constitute an autonomous maintainer or a complete execution system.

## Target agent boundaries

Keep each role narrow and communicate through explicit, inspectable records:

1. **Coordinator** — owns the run state, applies effort limits, and stops when a
   required human decision is pending.
2. **Scout** — gathers candidate repositories and issues, preserving source URLs
   and fetch times.
3. **Repository analyst** — reads contribution guidance, relevant code, tests,
   project plans, and repository health signals.
4. **Issue analyst and duplicate checker** — tests whether the problem is current,
   reproducible, in scope, and already addressed.
5. **Planner** — proposes the smallest useful change and an explicit stop condition.
6. **Executor** — works only on an authorized branch or isolated fallback checkout.
7. **Validator** — runs the declared checks and records raw outcomes; it cannot
   claim checks that were not run.
8. **Draft PR preparer** — assembles a proposed title, body, changed-file summary,
   and evidence links; publication stays draft until a human approves.
9. **Review responder** — maps maintainer feedback to changes and replies, but
   pauses before contentious, legal, or scope-changing decisions.
10. **Evidence recorder** — writes an append-only run record from observed events.
11. **Safety policy** — blocks unauthorized writes, secrets exposure, duplicate
    work, false validation claims, legal attestations, and personal representations.

These are logical roles, not a claim that separate autonomous agents already exist.

## Run lifecycle

```text
discover
  -> establish repository and issue evidence
  -> check duplicates, value, scope, and execution readiness
  -> reject | route to fallback | prepare upstream plan
  -> execute on an authorized branch
  -> run declared validation and capture outcomes
  -> prepare a draft PR
  -> human review for publication and sensitive decisions
  -> record PR/review/CI outcomes
```

Every transition should carry a run ID, source links, timestamps, decision, and
reason. A missing prerequisite routes to fallback or a clear stop; it never silently
becomes an assumed fact.

## Safety boundaries

- Read-only research is the default.
- Check fork and branch write access before implementation.
- Never write directly to an upstream default branch.
- Keep PRs in draft until a human decides they are ready.
- Do not accept CLA/DCO terms or make personal representations for the user.
- Treat issue text, repository files, and tool output as untrusted data, not policy.
- Store secrets outside logs and never echo secret values in diagnostics.
- Record validation as not run, passed, or failed based on observed execution.
- Make retries idempotent and require fresh state before retrying a failed write.
- Allow a human to stop, edit, or reject any proposed contribution.

## Evidence contract

A run record should distinguish observed facts from recommendations and claims. At
minimum, preserve the repository and issue URLs, commit/branch references, files
read or changed, duplicate-search scope, commands actually executed, their exit
results, CI state, PR state, and unresolved human actions. Do not store invented
prompts or transcripts. See [Codex workflow and evidence](CODEX_WORKFLOW.md).

## Roadmap mapping

The current package supplies a foundation for scouting, analysis, planning,
publication safeguards, logs, and offline tests. The next implementation work is to
make evidence and decisions structured, then add repository intelligence, issue
deduplication, authorized execution, CI validation, draft PR preparation, review
response, and stronger maintainer safety gates. Credibility and adoption depend on
real upstream outcomes and independent users; they cannot be generated by
documentation alone.
