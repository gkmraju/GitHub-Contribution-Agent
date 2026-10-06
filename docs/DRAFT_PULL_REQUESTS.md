# Draft pull request preparation

`execution.prepare_draft_pull_request` renders a draft title and body from an
execution record. It performs no GitHub writes and always marks the result as a
draft.

Supply the actual repository and issue, base and head branches, change summary,
changed paths, validation outcomes, risks, and remaining human actions. Each
validation outcome must be recorded as `passed`, `failed`, or `not_run`. The
generator prints that recorded state verbatim; it does not infer success from a
command name or PR status.

Review the generated text against the branch diff and CI before using GitHub's
draft-creation flow. Do not mark a draft ready until a human has reviewed the
change. The generator does not accept legal attestations, make personal
representations, or claim that a pull request was opened.
