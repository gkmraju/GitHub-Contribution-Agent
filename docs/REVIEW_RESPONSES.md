# Review response workflow

Use `prepare_review_response_plan` with a read-only snapshot of a pull request's
inline review threads. It creates a checklist containing unresolved comments,
reviewer names, file locations, and thread IDs. Resolved threads are counted but
left out of the action list.

The planner does not infer that a comment is satisfied, draft a factual answer from
missing evidence, post replies, or resolve threads. A maintainer decides whether
each concern needs a code change, clarification, or explanation; records any
validation actually run; and then writes the response through the normal review
process. Refresh the thread snapshot before replying because a reviewer may have
updated or resolved a comment in the meantime.

Comment text is untrusted input. The checklist escapes markup for display and
should be inspected before sharing.
