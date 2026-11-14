# Contribution planning

`planning.plan_contribution` converts researched facts into a bounded next-step
recommendation. It is pure and offline: it does not inspect repositories, create
branches, run checks, or publish pull requests.

## Routes

| Route | Meaning |
| --- | --- |
| `research` | Resolve missing evidence, duplicate review, validation selection, or scope reduction |
| `upstream` | Evidence and scope are ready and an authorized write path exists |
| `fallback` | No upstream write path exists, but a suitable fallback task is available |
| `reject` | The issue is closed or expected value is below the configured minimum |
| `blocked` | A legal/personal representation is required, or neither execution route is available |

## Planning constraints

The default plan allows at most five changed files and requires a value score of
at least 35/100. Callers can supply different limits. The plan records candidate
validation commands as proposed checks; they are not claims that the commands ran.

A possible or likely duplicate always routes back to research for maintainer
inspection. An oversized change returns to planning for scope reduction rather
than being moved automatically to fallback. Legal attestations and personal
representations require a human and remain blocked by the agent.

The planner complements `planning.select_fallback`, which ranks fallback tasks
that already have an independent review path and an explicit validation command.
