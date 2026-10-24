# Codex workflow and evidence

This repository documents a real contribution workflow. It does not manufacture
prompt transcripts, Codex logs, tool attribution, or claims about who performed
work.

## Evidence standard

A public pull request proves that a contribution was proposed and records what its
description says. It does not, by itself, prove which application, model, or person
performed each part of the work. A model name in a PR description is not proof that
Codex was used.

Use these labels precisely:

- **Repository artifact**: a commit, dated report, issue, or pull request that can be
  opened and inspected.
- **AI assistance disclosed**: the PR description names an AI tool or model.
- **Codex task evidence**: a contemporaneous Codex task record that identifies the
  repository and work, and can be linked or otherwise verified by its owner.
- **Unverified attribution**: anything inferred from a model name, writing style,
  or later recollection without a supporting record.

Never upgrade one label into another.

## Existing public records

These records demonstrate repository work and upstream contribution activity:

- [Initialize responsible daily contribution workflow](https://github.com/gkmraju/GitHub-Contribution-Agent/pull/1) establishes the original workflow, safety rules, tests, CI, and a dated research trail.
- [Add fork-aware repository health audit](https://github.com/gkmraju/GitHub-Contribution-Agent/pull/4) describes a read-only repository audit and its stated validation.
- [Fix unsafe request-scoped header values in DeerFlow](https://github.com/bytedance/deer-flow/pull/5085) records an AI-assistance disclosure naming OpenAI GPT-5.6 Sol.
- [Recognize repo-relative Dart test paths in GitNexus](https://github.com/abhigyanpatwari/GitNexus/pull/3058) is a public contribution record. Its PR description does not establish Codex provenance.
- [Accept artwork URLs in OpenCLI downloads](https://github.com/jackwener/OpenCLI/pull/2517) is a public contribution record. Its PR description does not establish Codex provenance.
- [Accept single-version npm array responses in Paperclip](https://github.com/paperclipai/paperclip/pull/12551) records a model-use disclosure naming OpenAI GPT-5.6 Sol with GitHub access and code-editing assistance. That disclosure does not by itself prove the Codex application was used.

PR titles, descriptions, and validation statements are reproduced as public records, not independently upgraded into claims about merge status or local execution.

## Recording future Codex-assisted work

For each future contribution, add or update a dated report only after the work
happens. Record:

1. Repository, issue, branch, commit, and PR links when they exist.
2. What the user asked Codex to do, in a short factual summary rather than an
   invented transcript.
3. Which parts were actually performed with Codex and which were performed by the
   user or another tool.
4. Exact validation commands and outcomes, or state clearly that validation was
   not run.
5. The publication state and any remaining human action.

Link a Codex task only when a real shareable task link exists and the owner chooses
to publish it. Do not publish private conversation content, credentials, or
machine-specific data to make an evidence trail look stronger.

## Current evidence boundary

This document was prepared in a Codex Work-mode conversation with GitHub repository
access. That fact describes this documentation session only. The public PR records
above do not establish Codex's role in those historical contributions. No test run
or upstream contribution is claimed by this documentation change.
