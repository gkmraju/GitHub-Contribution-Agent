# Reproducible contribution case studies

These are reconstructions from public issue and pull request records, not claims
that this repository executed the upstream changes. Reproduction means a reader
can inspect the source evidence and follow the same analysis and validation plan.
The upstream PR records state that executable checks were not run locally through
the connected integration; this document does not upgrade those statements.

## Paperclip: accept one unambiguous npm version

**Evidence:** [issue #12226](https://github.com/paperclipai/paperclip/issues/12226) and
[PR #12551](https://github.com/paperclipai/paperclip/pull/12551).

The issue reports that npm returned a JSON array containing exactly one version,
which prevented the installer from resolving the package version. The PR says it
accepts exactly one string in an array while retaining string behavior and
rejecting empty, non-string, or multiple entries. The issue was open and the PR
was open at the time this evidence was collected.

**Reproduction checklist**

1. Read the issue's minimal observed response and expected behavior.
2. Inspect the parser and its existing tests at the PR's base revision.
3. Add tests for a plain string, a one-string array, an empty array, a non-string
   item, and a multi-item array.
4. Change only the response normalization boundary.
5. Run the focused parser tests and relevant package validation; record command,
   exit status, and CI run links.
6. Compare the final diff with the issue and check for overlapping PRs before
   asking for maintainer review.

The PR description records that focused regression coverage was added but local
tests and lint were not run through the connected integration. It does not claim
those checks passed. Reproduction by this project's readers remains unverified.

## DeerFlow: reject unsafe request-scoped HTTP headers

**Evidence:** [issue #5065](https://github.com/bytedance/deer-flow/issues/5065) and
[PR #5085](https://github.com/bytedance/deer-flow/pull/5085).

The issue documents that malformed request-scoped credentials, such as values
with newlines or unsupported characters, can cause transport errors that echo
the credential into model-visible errors and persisted traces. The PR describes
pre-validating values, returning errors that identify the configured key without
including its value, and adding regression coverage. The issue is marked completed
and the PR is closed; closure alone is not used here as proof of merge.

**Reproduction checklist**

1. Inspect the issue's safe reproduction and the request-scoped header resolver.
2. Identify all credential ingress paths and where transport exceptions are
   converted into model-visible messages.
3. Add regression cases for CR, LF, NUL, surrounding whitespace, and values that
   cannot be encoded as Latin-1.
4. Assert every rejection message identifies the configured key but never
   contains the supplied secret.
5. Run focused tests and relevant CI; inspect error, trace, and checkpoint
   surfaces using a non-secret sentinel.
6. Verify the final patch does not log or serialize the rejected value.

The upstream PR description explicitly says executable tests and lint were not run
locally through the connected integration. The issue and PR remain independently
inspectable evidence; this repository has not rerun them.

## Evidence rules

For each future case, retain links to the issue, base revision, proposed commit,
PR, exact validation commands and observed results, CI run, and current review
state. Label missing checks as not run. Do not turn an open issue into a solved
case, infer merge status from closure, or claim Codex provenance from an AI model
disclosure.
