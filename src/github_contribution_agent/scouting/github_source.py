"""Read-only GitHub REST collection for repository health audits."""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from github_contribution_agent.analysis.repo_health import RepoSnapshot


class GitHubAPIError(RuntimeError):
    """A bounded, credential-safe GitHub API failure."""


class GitHubClient:
    def __init__(
        self,
        *,
        token: str | None = None,
        base_url: str = "https://api.github.com",
        timeout: float = 20.0,
    ) -> None:
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    @classmethod
    def from_environment(cls) -> GitHubClient:
        return cls(token=os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))

    def get_json(self, path: str, *, params: dict[str, str | int] | None = None) -> Any:
        query = f"?{urlencode(params)}" if params else ""
        request = Request(
            f"{self._base_url}{path}{query}",
            headers=self._headers(),
            method="GET",
        )
        try:
            with urlopen(request, timeout=self._timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise GitHubAPIError(
                f"GitHub API request failed with HTTP {error.code}: {path}"
            ) from error
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise GitHubAPIError(f"GitHub API request failed: {path}") from error

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "github-contribution-agent",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers


def collect_owned_repositories(
    owner: str, *, client: GitHubClient | None = None
) -> tuple[RepoSnapshot, ...]:
    """Collect repository metadata, file inventory, and fork divergence read-only."""
    client = client or GitHubClient.from_environment()
    repositories = _list_owned_repositories(owner, client)
    snapshots: list[RepoSnapshot] = []
    for repository in repositories:
        name = str(repository["name"])
        full_name = str(repository["full_name"])
        default_branch = str(repository.get("default_branch") or "main")
        files: tuple[str, ...] = ()
        inspection_complete = True
        try:
            tree = client.get_json(
                f"/repos/{full_name}/git/trees/{quote(default_branch, safe='')}",
                params={"recursive": 1},
            )
            files = tuple(
                item["path"]
                for item in tree.get("tree", ())
                if item.get("type") == "blob" and "path" in item
            )
            inspection_complete = not bool(tree.get("truncated", False))
        except GitHubAPIError:
            inspection_complete = False

        upstream_full_name = None
        ahead_by = None
        behind_by = None
        if repository.get("fork"):
            try:
                details = client.get_json(f"/repos/{full_name}")
                parent = details.get("parent") or {}
                upstream_full_name = parent.get("full_name")
                parent_branch = parent.get("default_branch")
                if upstream_full_name and parent_branch:
                    comparison = client.get_json(
                        f"/repos/{upstream_full_name}/compare/"
                        f"{quote(str(parent_branch), safe='')}..."
                        f"{quote(owner, safe='')}:{quote(default_branch, safe='')}"
                    )
                    ahead_by = int(comparison.get("ahead_by", 0))
                    behind_by = int(comparison.get("behind_by", 0))
            except GitHubAPIError:
                pass

        snapshots.append(
            RepoSnapshot.from_mapping(
                {
                    "owner": owner,
                    "name": name,
                    "html_url": repository.get("html_url", ""),
                    "default_branch": default_branch,
                    "pushed_at": repository.get("pushed_at"),
                    "files": files,
                    "fork": repository.get("fork", False),
                    "archived": repository.get("archived", False),
                    "upstream_full_name": upstream_full_name,
                    "upstream_ahead_by": ahead_by,
                    "upstream_behind_by": behind_by,
                    "inspection_complete": inspection_complete,
                }
            )
        )
    return tuple(snapshots)


def _list_owned_repositories(owner: str, client: GitHubClient) -> list[dict[str, Any]]:
    repositories: list[dict[str, Any]] = []
    for page in range(1, 11):
        batch = client.get_json(
            f"/users/{quote(owner, safe='')}/repos",
            params={"type": "owner", "sort": "updated", "per_page": 100, "page": page},
        )
        repositories.extend(batch)
        if len(batch) < 100:
            break
    return repositories
