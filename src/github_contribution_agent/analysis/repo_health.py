"""Transparent, fork-aware repository health scoring and recommendations."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import PurePosixPath
from typing import Any


@dataclass(frozen=True, slots=True)
class RepoSnapshot:
    """Read-only repository facts collected before optimization decisions."""

    owner: str
    name: str
    html_url: str
    default_branch: str
    pushed_at: datetime | None
    files: tuple[str, ...]
    fork: bool = False
    archived: bool = False
    upstream_full_name: str | None = None
    upstream_ahead_by: int | None = None
    upstream_behind_by: int | None = None
    purposeful_divergence: bool = False
    inspection_complete: bool = True

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.name}"

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> RepoSnapshot:
        pushed_at = value.get("pushed_at")
        if isinstance(pushed_at, str):
            pushed_at = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        if pushed_at is not None and pushed_at.tzinfo is None:
            pushed_at = pushed_at.replace(tzinfo=UTC)

        return cls(
            owner=str(value["owner"]),
            name=str(value["name"]),
            html_url=str(value.get("html_url", "")),
            default_branch=str(value.get("default_branch", "main")),
            pushed_at=pushed_at,
            files=tuple(str(path) for path in value.get("files", ())),
            fork=bool(value.get("fork", False)),
            archived=bool(value.get("archived", False)),
            upstream_full_name=value.get("upstream_full_name"),
            upstream_ahead_by=_optional_int(value.get("upstream_ahead_by")),
            upstream_behind_by=_optional_int(value.get("upstream_behind_by")),
            purposeful_divergence=bool(value.get("purposeful_divergence", False)),
            inspection_complete=bool(value.get("inspection_complete", True)),
        )


@dataclass(frozen=True, slots=True)
class HealthScores:
    """Component scores use 0 as weakest and 100 as healthiest."""

    activity: int
    ci: int
    tests: int
    docs: int
    dependencies: int
    security_config: int
    staleness: int
    fork_divergence: int


@dataclass(frozen=True, slots=True)
class RepositoryAudit:
    repository: RepoSnapshot
    scores: HealthScores
    overall_score: int
    priority: int
    opportunities: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        repository = asdict(self.repository)
        if self.repository.pushed_at is not None:
            repository["pushed_at"] = self.repository.pushed_at.isoformat()
        return {
            "repository": repository,
            "scores": asdict(self.scores),
            "overall_score": self.overall_score,
            "priority": self.priority,
            "opportunities": list(self.opportunities),
        }


_WEIGHTS = {
    "activity": 0.15,
    "ci": 0.15,
    "tests": 0.15,
    "docs": 0.10,
    "dependencies": 0.15,
    "security_config": 0.15,
    "staleness": 0.10,
    "fork_divergence": 0.05,
}

_SOURCE_SUFFIXES = {
    ".c",
    ".cpp",
    ".cs",
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".swift",
    ".ts",
    ".tsx",
}

_MANIFESTS = {
    "cargo.toml",
    "composer.json",
    "gemfile",
    "go.mod",
    "package.json",
    "pom.xml",
    "pyproject.toml",
    "requirements.txt",
}

_LOCKFILES = {
    "bun.lock",
    "bun.lockb",
    "cargo.lock",
    "composer.lock",
    "gemfile.lock",
    "package-lock.json",
    "pnpm-lock.yaml",
    "poetry.lock",
    "uv.lock",
    "yarn.lock",
}


def audit_repository(
    repository: RepoSnapshot,
    *,
    as_of: datetime | None = None,
) -> RepositoryAudit:
    """Score one repository and produce independently reviewable opportunities."""
    as_of = _aware_utc(as_of or datetime.now(UTC))
    days_since_push = _days_since(repository.pushed_at, as_of)
    paths = {path.casefold() for path in repository.files}
    basenames = {PurePosixPath(path).name for path in paths}

    activity = _activity_score(days_since_push)
    staleness = _staleness_score(days_since_push)
    fork_divergence = _fork_divergence_score(repository)
    code_repository = any(
        PurePosixPath(path).suffix in _SOURCE_SUFFIXES for path in paths
    )

    if repository.fork and not repository.purposeful_divergence:
        ci = tests = docs = dependencies = security_config = 100
    else:
        ci = 100 if _has_workflow(paths) or not code_repository else 0
        tests = 100 if _has_tests(paths) or not code_repository else 0
        docs = _docs_score(paths, basenames)
        dependencies = _dependency_score(paths, basenames, code_repository)
        security_config = _security_score(paths, basenames, code_repository)

    scores = HealthScores(
        activity=activity,
        ci=ci,
        tests=tests,
        docs=docs,
        dependencies=dependencies,
        security_config=security_config,
        staleness=staleness,
        fork_divergence=fork_divergence,
    )
    overall = round(
        sum(
            getattr(scores, component) * weight
            for component, weight in _WEIGHTS.items()
        )
    )
    opportunities = _opportunities(
        repository,
        scores,
        code_repository=code_repository,
        days_since_push=days_since_push,
        paths=paths,
        basenames=basenames,
    )
    priority = 0 if repository.archived else 100 - overall
    if not opportunities:
        priority = 0
    return RepositoryAudit(repository, scores, overall, priority, opportunities)


def audit_repositories(
    repositories: Iterable[RepoSnapshot],
    *,
    as_of: datetime | None = None,
) -> tuple[RepositoryAudit, ...]:
    """Return repositories ranked by optimization priority, then by name."""
    audits = [audit_repository(repo, as_of=as_of) for repo in repositories]
    return tuple(
        sorted(
            audits,
            key=lambda audit: (
                -audit.priority,
                audit.overall_score,
                audit.repository.full_name.casefold(),
            ),
        )
    )


def render_markdown(audits: Iterable[RepositoryAudit], *, owner: str) -> str:
    """Render a durable, human-readable ranked opportunity report."""
    rows = tuple(audits)
    lines = [
        f"# Repository health audit: {owner}",
        "",
        "Scores run from 0 (weak) to 100 (healthy). Priority ranks actionable gaps; archived repositories stay at priority 0.",
        "",
        "| Rank | Repository | Kind | Health | Priority | Top opportunity |",
        "| ---: | --- | --- | ---: | ---: | --- |",
    ]
    for rank, audit in enumerate(rows, start=1):
        repo = audit.repository
        kind = "fork" if repo.fork else "original"
        top = audit.opportunities[0] if audit.opportunities else "No action recommended"
        lines.append(
            f"| {rank} | [{repo.full_name}]({repo.html_url}) | {kind} | "
            f"{audit.overall_score} | {audit.priority} | {top} |"
        )

    for audit in rows:
        if not audit.opportunities:
            continue
        lines.extend(["", f"## {audit.repository.full_name}", ""])
        lines.extend(f"- {opportunity}" for opportunity in audit.opportunities)
    return "\n".join(lines) + "\n"


def render_json(audits: Iterable[RepositoryAudit]) -> str:
    return (
        json.dumps(
            {"repositories": [audit.to_dict() for audit in audits]},
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def _opportunities(
    repository: RepoSnapshot,
    scores: HealthScores,
    *,
    code_repository: bool,
    days_since_push: int | None,
    paths: set[str],
    basenames: set[str],
) -> tuple[str, ...]:
    if repository.archived:
        return (
            "repository is archived; retain it read-only unless revival is intentional",
        )
    if repository.fork and not repository.purposeful_divergence:
        return _fork_opportunities(repository, days_since_push)

    opportunities: list[str] = []
    if not repository.inspection_complete:
        opportunities.append("retry the file inventory before making code changes")
    if code_repository and scores.ci < 100:
        opportunities.append(
            "add a minimal CI workflow that runs the repository's real validation"
        )
    if code_repository and scores.tests < 100:
        opportunities.append("add deterministic tests around the highest-risk behavior")
    if scores.docs < 100:
        if "readme.md" not in basenames:
            opportunities.append(
                "add a README with purpose, setup, validation, and project boundaries"
            )
        elif not any(name.startswith("license") for name in basenames):
            opportunities.append("clarify reuse terms with an appropriate license")
        else:
            opportunities.append(
                "add contribution guidance for independently reviewable changes"
            )
    if code_repository and scores.dependencies < 100:
        if not (_MANIFESTS & basenames):
            opportunities.append(
                "declare runtime dependencies in the ecosystem's standard manifest"
            )
        else:
            opportunities.append(
                "add reproducible dependency locking or automated update checks where appropriate"
            )
    if code_repository and scores.security_config < 100:
        if ".gitignore" not in basenames:
            opportunities.append(
                "add ignore rules for credentials, local environments, and generated files"
            )
        elif ".github/dependabot.yml" not in paths and "renovate.json" not in basenames:
            opportunities.append("add automated dependency update configuration")
        elif "security.md" not in basenames:
            opportunities.append("document the repository's security reporting policy")
        else:
            opportunities.append(
                "add CODEOWNERS in the repository root, .github, or docs directory"
            )
    if scores.staleness <= 25:
        opportunities.append(
            "decide explicitly whether to revive, document, or archive this stale repository"
        )
    return tuple(dict.fromkeys(opportunities))


def _fork_opportunities(
    repository: RepoSnapshot, days_since_push: int | None
) -> tuple[str, ...]:
    opportunities: list[str] = []
    if repository.upstream_behind_by is None:
        opportunities.append("assess upstream divergence before changing this fork")
    elif repository.upstream_behind_by > 0:
        opportunities.append(
            f"sync or assess the fork: {repository.upstream_behind_by} upstream commits behind"
        )
    if repository.upstream_ahead_by:
        opportunities.append(
            f"review {repository.upstream_ahead_by} ahead commits and record whether divergence is purposeful"
        )
    if days_since_push is None or days_since_push > 730:
        opportunities.append("archive the fork if it has no active, documented purpose")
    if not opportunities:
        opportunities.append("record the fork's purpose; otherwise leave it unchanged")
    return tuple(opportunities)


def _activity_score(days_since_push: int | None) -> int:
    if days_since_push is None:
        return 0
    if days_since_push <= 30:
        return 100
    if days_since_push <= 90:
        return 70
    if days_since_push <= 180:
        return 40
    if days_since_push <= 365:
        return 20
    return 0


def _staleness_score(days_since_push: int | None) -> int:
    if days_since_push is None:
        return 0
    if days_since_push <= 90:
        return 100
    if days_since_push <= 180:
        return 75
    if days_since_push <= 365:
        return 50
    if days_since_push <= 730:
        return 25
    return 0


def _fork_divergence_score(repository: RepoSnapshot) -> int:
    if not repository.fork:
        return 100
    if repository.upstream_behind_by is None:
        return 25
    behind = repository.upstream_behind_by
    if behind == 0:
        return 100
    if behind <= 10:
        return 70
    if behind <= 50:
        return 40
    return 10


def _docs_score(paths: set[str], basenames: set[str]) -> int:
    score = 0
    if "readme.md" in basenames:
        score += 60
    if any(name.startswith("license") for name in basenames):
        score += 25
    if "contributing.md" in basenames:
        score += 15
    return score


def _dependency_score(
    paths: set[str], basenames: set[str], code_repository: bool
) -> int:
    if not code_repository:
        return 100
    if not (_MANIFESTS & basenames):
        return 0
    automated = ".github/dependabot.yml" in paths or "renovate.json" in basenames
    return 100 if (_LOCKFILES & basenames) or automated else 70


def _security_score(paths: set[str], basenames: set[str], code_repository: bool) -> int:
    if not code_repository:
        return 100
    score = 0
    if ".gitignore" in basenames:
        score += 40
    if "security.md" in basenames:
        score += 30
    if ".github/dependabot.yml" in paths or "renovate.json" in basenames:
        score += 20
    if "codeowners" in basenames:
        score += 10
    return score


def _has_workflow(paths: set[str]) -> bool:
    return any(
        path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml"))
        for path in paths
    )


def _has_tests(paths: set[str]) -> bool:
    return any(
        path.startswith(("test/", "tests/"))
        or "/__tests__/" in path
        or PurePosixPath(path).name.startswith("test_")
        or PurePosixPath(path).name.endswith(
            (".test.js", ".test.ts", ".spec.js", ".spec.ts")
        )
        for path in paths
    )


def _days_since(pushed_at: datetime | None, as_of: datetime) -> int | None:
    if pushed_at is None:
        return None
    return max(0, (_aware_utc(as_of) - _aware_utc(pushed_at)).days)


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _optional_int(value: Any) -> int | None:
    return None if value is None else int(value)
