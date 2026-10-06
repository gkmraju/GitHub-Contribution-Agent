# Contributing

Thanks for considering a contribution. This project is safety-first: useful,
reviewable behavior matters more than activity volume.

## Before you start

- Read the [architecture](docs/ARCHITECTURE.md), [Codex evidence policy](docs/CODEX_WORKFLOW.md),
  and [maintainer safety gates](docs/MAINTAINER_SAFETY.md).
- For a behavior change, open or reference an issue and check for duplicate work.
- Keep changes focused and explain the user-facing problem they solve.
- Do not include credentials, private prompts, user data, or fabricated evidence.

## Development

Python 3.11 or newer is required. Install the package in editable mode:

```console
python -m pip install -e .
```

Run the checks before proposing a change:

```console
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

In your pull request, list the exact checks run and their outcomes. Clearly label
checks you could not run. Hosted CI results should be linked to the tested commit.

## Pull requests

Use the pull request template to describe evidence, scope, validation, risks, and
remaining work. Keep the PR in draft until a human maintainer decides it is ready.
Reviewers may request changes or close work that is duplicate, speculative,
unsafe, or outside project scope. No contributor is expected to accept legal
terms or make personal representations on another person's behalf.

Contributions may use AI assistance, but tool or model attribution must be factual.
A model disclosure is not evidence that a particular application was used. See
the [evidence policy](docs/CODEX_WORKFLOW.md).
