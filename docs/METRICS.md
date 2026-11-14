# Maintainer process metrics

After structured audit events are available, summarize a local JSONL file with:

```console
PYTHONPATH=src python -m github_contribution_agent.metrics logs/runtime/events.jsonl
```

The report counts events, unique run IDs, recorded decision labels, event types,
and validation outcomes (`passed`, `failed`, `not_run`). It describes only what
the event file records. A run may create multiple events, and a missing event is
not proof that an action did not happen.

These are process measures, not quality or impact measures. They do not measure
maintainer time saved, accepted contributions, adoption, or user satisfaction.
Those require separately collected, auditable outcome data and an agreed
measurement method. Never report an empty audit file as zero activity for the
project as a whole.
