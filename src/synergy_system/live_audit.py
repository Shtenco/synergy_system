from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Protocol

from .validator import FederationError


class LiveAuditAuthRequired(FederationError):
    pass


class RepoMetadataProvider(Protocol):
    def repository(self, full_name: str) -> dict[str, Any]: ...


@dataclass(frozen=True)
class GitHubRestProvider:
    token: str
    api_base: str = "https://api.github.com"
    timeout_seconds: int = 10

    def __post_init__(self) -> None:
        if not self.token:
            raise LiveAuditAuthRequired("read-only GitHub token/app credential is required for private-repository audit")
        if self.api_base != "https://api.github.com":
            raise FederationError("v1 live audit only supports api.github.com")
        if isinstance(self.timeout_seconds, bool) or not isinstance(self.timeout_seconds, int) or not (1 <= self.timeout_seconds <= 60):
            raise FederationError("invalid audit timeout")

    def repository(self, full_name: str) -> dict[str, Any]:
        if not full_name.startswith("Shtenco/") or full_name.count("/") != 1:
            raise FederationError("live audit repository name must be explicit Shtenco/name")
        owner, name = full_name.split("/", 1)
        url = f"{self.api_base}/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(name)}"
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "SYNERGY-System-Live-Audit/1",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read(2 * 1024 * 1024 + 1)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise FileNotFoundError(full_name) from exc
            raise FederationError(f"GitHub API HTTP {exc.code} while auditing {full_name}") from exc
        except Exception as exc:
            raise FederationError(f"GitHub API request failed for {full_name}: {type(exc).__name__}") from exc
        if len(raw) > 2 * 1024 * 1024:
            raise FederationError("GitHub repository metadata response unexpectedly large")
        try:
            value = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise FederationError("invalid GitHub repository metadata JSON") from exc
        if not isinstance(value, dict):
            raise FederationError("GitHub repository metadata must be object")
        return value


def audit_repositories(
    expected_repositories: set[str],
    provider: RepoMetadataProvider,
    *,
    observed_at: str | None = None,
) -> dict[str, Any]:
    if not expected_repositories:
        raise FederationError("expected repository set is empty")
    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for full_name in sorted(expected_repositories):
        try:
            metadata = provider.repository(full_name)
        except FileNotFoundError:
            missing.append(full_name)
            continue
        if metadata.get("full_name") != full_name:
            raise FederationError(f"GitHub metadata full_name mismatch for {full_name}")
        default_branch = metadata.get("default_branch")
        if not isinstance(default_branch, str) or not default_branch:
            raise FederationError(f"missing default_branch for {full_name}")
        private = metadata.get("private")
        archived = metadata.get("archived")
        disabled = metadata.get("disabled")
        if not all(isinstance(value, bool) for value in (private, archived, disabled)):
            raise FederationError(f"invalid boolean metadata for {full_name}")
        rows.append({
            "repo": full_name,
            "default_branch": default_branch,
            "private": private,
            "archived": archived,
            "disabled": disabled,
        })

    stamp = observed_at or datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    _utc(stamp)
    payload = {
        "schema": "synergy.repository-live-audit/v1",
        "observed_at": stamp,
        "expected_repository_count": len(expected_repositories),
        "observed_repository_count": len(rows),
        "missing_repositories": missing,
        "repositories": rows,
        "audit_status": "COMPLETE" if not missing and len(rows) == len(expected_repositories) else "INCOMPLETE",
        "architecture_authority": "NONE",
        "execution_authority": "NONE",
    }
    digest = hashlib.sha256(_canonical(payload)).hexdigest()
    return payload | {"digest": digest}


def verify_live_audit(payload: dict[str, Any], expected_repositories: set[str]) -> None:
    expected_fields = {
        "schema", "observed_at", "expected_repository_count", "observed_repository_count",
        "missing_repositories", "repositories", "audit_status", "architecture_authority",
        "execution_authority", "digest"
    }
    if set(payload) != expected_fields or payload["schema"] != "synergy.repository-live-audit/v1":
        raise FederationError("live audit shape/schema mismatch")
    _utc(payload["observed_at"])
    for field in ("expected_repository_count", "observed_repository_count"):
        value = payload[field]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0 or value > 2**53 - 1:
            raise FederationError(f"invalid {field}")
    if payload["expected_repository_count"] != len(expected_repositories):
        raise FederationError("live audit expected repository count mismatch")
    rows = payload["repositories"]
    if not isinstance(rows, list):
        raise FederationError("live audit repositories must be list")
    names = [row.get("repo") for row in rows if isinstance(row, dict)]
    if names != sorted(names) or len(names) != len(set(names)):
        raise FederationError("live audit repository rows must be sorted and unique")
    missing = payload["missing_repositories"]
    if not isinstance(missing, list) or missing != sorted(set(missing)):
        raise FederationError("missing repository list must be sorted unique")
    if set(names) | set(missing) != expected_repositories or set(names) & set(missing):
        raise FederationError("live audit repository partition mismatch")
    expected_status = "COMPLETE" if not missing and len(names) == len(expected_repositories) else "INCOMPLETE"
    if payload["audit_status"] != expected_status:
        raise FederationError("live audit status mismatch")
    if payload["architecture_authority"] != "NONE" or payload["execution_authority"] != "NONE":
        raise FederationError("live audit cannot grant authority")
    body = dict(payload)
    supplied = body.pop("digest")
    if not isinstance(supplied, str) or len(supplied) != 64 or supplied != hashlib.sha256(_canonical(body)).hexdigest():
        raise FederationError("live audit digest mismatch")


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _utc(value: Any) -> None:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise FederationError("timestamp must use UTC Z form")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise FederationError("invalid timestamp") from exc
    if parsed.tzinfo != timezone.utc:
        raise FederationError("timestamp must be UTC")
