"""Deterministic maintainer approval and scope checks for agent execution."""

from dataclasses import dataclass
from pathlib import PurePosixPath


_BLOCKED_PARTS = {".git", "secrets", "credentials"}
_BLOCKED_NAMES = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"}


@dataclass(frozen=True, slots=True)
class ExecutionRequest:
    repository: str
    expected_repository: str
    base_ref: str
    base_sha: str
    changed_paths: tuple[str, ...]
    allowed_paths: tuple[str, ...]
    approved_by_maintainer: bool = False
    max_files: int = 10


def validate_execution_request(request: ExecutionRequest) -> tuple[str, ...]:
    """Return blocking reasons; an empty tuple means the request meets policy.

    This is a preflight check only. It does not grant GitHub permissions, execute
    commands, or replace review of the proposed patch.
    """
    violations: list[str] = []
    if not request.approved_by_maintainer:
        violations.append("explicit maintainer approval is required")
    if not request.expected_repository or request.repository.casefold() != request.expected_repository.casefold():
        violations.append("repository identity does not match the approved repository")
    if not request.base_ref or request.base_ref.casefold() in {"main", "master"}:
        violations.append("execution must target a non-default feature branch")
    if not request.base_sha:
        violations.append("base commit SHA must be pinned")
    if request.max_files < 1:
        violations.append("maximum file count must be positive")
    if len(request.changed_paths) > request.max_files:
        violations.append("changed file count exceeds the approved limit")
    if not request.changed_paths:
        violations.append("at least one changed path must be declared")

    allowed = tuple(_normalize(path) for path in request.allowed_paths)
    for raw_path in request.changed_paths:
        path = _normalize(raw_path)
        if not path:
            violations.append("changed paths must be relative and non-empty")
            continue
        if _is_sensitive(path):
            violations.append(f"sensitive path is blocked: {raw_path}")
        if not any(path == root or path.startswith(root.rstrip("/") + "/") for root in allowed):
            violations.append(f"path is outside the approved scope: {raw_path}")
    return tuple(violations)


def _normalize(path: str) -> str:
    if not path or "\\" in path or path.startswith("/") or ":" in path:
        return ""
    parts = PurePosixPath(path).parts
    if any(part in {".", ".."} for part in parts):
        return ""
    return "/".join(parts).casefold()


def _is_sensitive(path: str) -> bool:
    parts = set(path.split("/"))
    if parts & _BLOCKED_PARTS or path == ".github/workflows" or path.startswith(".github/workflows/"):
        return True
    if parts & _BLOCKED_NAMES or any(part.startswith(".env.") for part in parts):
        return True
    return False
