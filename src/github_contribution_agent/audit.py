"""Append privacy-conscious, structured contribution run events as JSONL."""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from urllib.parse import parse_qsl, urlsplit


_SECRET_PATTERNS = (
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bBearer\s+\S+", re.IGNORECASE),
)
_SENSITIVE_QUERY_KEYS = {"access_token", "api_key", "key", "secret", "token"}


@dataclass(frozen=True, slots=True)
class AuditValidation:
    command: str
    state: str
    exit_code: int | None = None


@dataclass(frozen=True, slots=True)
class AuditEvent:
    event_id: str
    run_id: str
    occurred_at: str
    event_type: str
    repository: str
    decision: str
    source_urls: tuple[str, ...] = ()
    issue_url: str = ""
    branch: str = ""
    commit: str = ""
    changed_paths: tuple[str, ...] = ()
    validations: tuple[AuditValidation, ...] = ()
    human_actions: tuple[str, ...] = ()

    def to_json_line(self) -> str:
        _validate_event(self)
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":")) + "\n"


def append_audit_event(path: str | Path, event: AuditEvent) -> None:
    """Append one validated event and flush it to disk.

    Records contain references and outcomes, not prompts, issue bodies, credentials,
    or raw command output. The file is append-oriented, not cryptographically
    tamper-proof; deployments needing stronger guarantees should export events to
    an access-controlled external audit store.
    """

    line = event.to_json_line()
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(line)
        stream.flush()
        os.fsync(stream.fileno())


def _validate_event(event: AuditEvent) -> None:
    if not event.event_id.strip() or not event.run_id.strip():
        raise ValueError("event_id and run_id are required")
    try:
        timestamp = datetime.fromisoformat(event.occurred_at.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("occurred_at must be an ISO-8601 timestamp") from error
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("occurred_at must include a timezone")
    if not event.event_type.strip() or not event.decision.strip():
        raise ValueError("event_type and decision are required")
    repository_parts = event.repository.split("/")
    if len(repository_parts) != 2 or any(not part for part in repository_parts):
        raise ValueError("repository must use owner/name format")
    if event.issue_url:
        _validate_url(event.issue_url)
    for url in event.source_urls:
        _validate_url(url)
    for path in event.changed_paths:
        parsed = PurePosixPath(path)
        if (
            not path
            or "\\" in path
            or parsed.is_absolute()
            or any(part in {"", ".", ".."} for part in path.split("/"))
        ):
            raise ValueError("changed paths must be repository-relative")
    for validation in event.validations:
        if not validation.command.strip():
            raise ValueError("validation command must not be empty")
        if validation.state not in {"passed", "failed", "not_run"}:
            raise ValueError("validation state must be passed, failed, or not_run")
        if validation.state == "passed" and validation.exit_code != 0:
            raise ValueError("passed validation requires exit_code 0")
        if validation.state == "failed" and (
            validation.exit_code is None or validation.exit_code == 0
        ):
            raise ValueError("failed validation requires a nonzero exit_code")
        if validation.state == "not_run" and validation.exit_code is not None:
            raise ValueError("not_run validation must not include an exit_code")
    _reject_secrets(asdict(event))


def _validate_url(value: str) -> None:
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError("source URLs must be HTTPS URLs without embedded credentials")
    if any(key.casefold() in _SENSITIVE_QUERY_KEYS for key, _ in parse_qsl(parsed.query)):
        raise ValueError("source URL must not contain credential query parameters")


def _reject_secrets(value: object) -> None:
    if isinstance(value, dict):
        for nested in value.values():
            _reject_secrets(nested)
    elif isinstance(value, (list, tuple)):
        for nested in value:
            _reject_secrets(nested)
    elif isinstance(value, str):
        if any(pattern.search(value) for pattern in _SECRET_PATTERNS):
            raise ValueError("audit fields must not contain credentials or bearer tokens")
