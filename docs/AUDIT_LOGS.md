# Structured audit events

The runtime audit writer appends one JSON record per line. Each event carries a
run ID, timestamp with timezone, event type, repository, decision, source links,
branch/commit, changed paths, observed validation states, and remaining human
actions.

The writer rejects credentials in structured fields, credential-bearing URL query
parameters, unsafe changed paths, and inconsistent validation outcomes. It never
accepts prompts, issue bodies, or raw command output. A validation is `passed`
only with exit code 0; an unrun validation has no exit code.

Runtime events should be written under `logs/runtime/`, which is ignored by Git.
Human-authored reports and case studies remain reviewable source files. This
append-oriented JSONL file is not a tamper-proof audit service: use restricted file
permissions and an external access-controlled store if stronger retention or
integrity controls are needed. Do not commit secrets or private issue content.
