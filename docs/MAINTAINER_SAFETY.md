# Maintainer safety gates

The execution preflight requires an explicit maintainer approval, exact approved
repository identity, a pinned base commit, a non-default feature branch, a
bounded changed-file count, and paths inside the declared scope. It rejects
absolute paths, traversal, credential files, environment files, Git internals,
and workflow definitions.

This policy is deterministic input validation. It does not execute a model or
command, grant repository permissions, establish that a patch is correct, or
replace human review. The agent should run it before any execution session and
again against the resulting changed-file list. A human maintainer remains
responsible for reviewing the diff and deciding whether to publish or merge.

The default limit is ten files and must be explicitly raised by the maintainer
when a justified task needs more. Approval should be captured in the task
record; the boolean supplied to this library is not an identity or signature.
