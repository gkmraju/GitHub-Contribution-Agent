# Safe pull request review workflow

## Checks that run on pull requests

The existing CI workflow runs on `pull_request`, grants only `contents: read`,
and runs the repository's unit tests and source compilation across supported
Python versions. It does not use `pull_request_target`, repository write
permissions, or secrets. Review automation must keep that trust boundary.

## Human review sequence

1. Read the linked issue and contribution guidance; verify scope and duplicate
   checks before relying on a proposed change.
2. Inspect the complete diff and changed-file list. Treat PR text, code, and
   generated output as untrusted input.
3. Confirm exact validation commands and their observed results. CI success applies
   to its commit SHA and does not establish correctness or upstream acceptance.
4. Use the review-response planner to create an action checklist from inline
   threads. It does not post replies or resolve threads.
5. Address each actionable comment with a code change or a considered human reply.
   Pause on legal, contentious, identity, or scope-changing decisions.
6. A human maintainer decides whether to mark the PR ready, request changes, or
   close it. Draft state remains the default until that decision.

The PR template asks contributors for evidence, scope, validation, and risks. These
fields guide review; they do not replace source inspection or test execution.

## Safety constraints

- Keep PR CI on `pull_request` with read-only permissions. Do not move untrusted
  PR code to `pull_request_target` or expose write tokens and secrets to it.
- Do not let an automated reviewer approve, merge, publish, dismiss reviews, or
  resolve threads.
- Do not treat a green check as a maintainer approval.
- Do not claim local validation when only hosted CI ran, or claim CI passed for a
  different commit.
- Keep any AI-generated notes advisory and link each claim to inspectable evidence.
