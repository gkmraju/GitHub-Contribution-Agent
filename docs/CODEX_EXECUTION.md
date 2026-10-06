# Codex execution adapter

The optional `execution.codex.create_codex_execution_session` adapter creates a
self-hosted session with the OpenAI Agents API Codex harness. The application does
not start the executor or publish repository changes. An operator starts the
separate `codex exec-server` process after reviewing the returned session details.

## Prerequisites

1. Install the optional SDK: `pip install -e ".[codex]"`.
2. Configure an OpenAI Platform application key outside the workspace with the
   Agents session and Responses permissions required by the OpenAI Agents API.
3. Install and authenticate Codex CLI in an isolated executor environment.
4. Set the executor's restricted environment key as `CODEX_API_KEY`; keep it
   separate from the application `OPENAI_API_KEY`.
5. Use an isolated checkout on a non-default branch. Do not expose GitHub write
   credentials to the executor.

The Agents API supports both OpenAI-hosted and self-hosted execution. This adapter
uses self-hosted execution so the operator controls the workspace. The API session
must connect to a running executor before work can access files. Follow the
[Agents API quickstart](https://developers.openai.com/api/docs/guides/agents-api/quickstart)
and [self-hosted sandbox guide](https://developers.openai.com/api/docs/guides/agents-api/environments/self-hosted)
for current setup and lifecycle details.

## Request and stop conditions

A request is rejected unless it has explicit human approval, an isolated workspace,
a non-default branch, a reviewed base revision, a non-empty allowed-path list, and
proposed validation commands. The prompt tells Codex to avoid branch changes,
commits, pushes, pull-request publication, legal terms, and personal
representations. The adapter does not attach GitHub write tools or credentials.

The path and branch checks are input validation, not an operating-system sandbox.
Isolation, network restrictions, executor lifetime, cost controls, and human
supervision must be enforced by the deployment environment. Keep the workspace
free of secrets. The Agents API documentation currently describes US data
residency and no Zero Data Retention support; review the current service terms
before sending private source or issue content.

The returned remote URL and environment ID are operational connection details.
Do not put them in public logs. The application records no prompt or source content
by default; record only the real session ID and outcome when an actual run occurs.
