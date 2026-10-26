# Public offline demo

This walkthrough uses a synthetic record and the real offline CLI. The repository
and issue URL use reserved example values; they are not real projects, issues, or
contribution evidence. The CLI reads the record and returns a route. It does not
search GitHub, inspect a repository, run an agent, change files, or publish
anything.

## Try it

From the repository root with Python 3.11 or newer:

```console
python -m pip install -e .
github-contribution-agent evaluate examples/demo-opportunity.json
```

Expected decision:

```json
{
  "reasons": [
    "contribution guide was not reviewed",
    "issue discussion was not reviewed",
    "repository conventions were not reviewed",
    "relevant files were not reviewed",
    "relevant tests were not identified",
    "scope is not clear",
    "no authorized fork or upstream write path is available"
  ],
  "route": "fallback"
}
```

The fallback decision is intentional: the sample has no evidence that the issue
was researched and no authorized write path. To evaluate a real opportunity,
first review its contribution guide, discussion, conventions, relevant code and
tests, establish a clear scope, and confirm an authorized branch or fork. Never
copy a synthetic example into a public contribution record.

See [the architecture](ARCHITECTURE.md), [Codex evidence policy](CODEX_WORKFLOW.md),
and [maintainer safety gates](MAINTAINER_SAFETY.md) for current limits and review
requirements.
