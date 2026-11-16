from __future__ import annotations

import json
import os
from pathlib import Path
import sys

from synergy_system.live_audit import GitHubRestProvider, LiveAuditAuthRequired, audit_repositories
from synergy_system.validator import load_expected_repositories


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    token = os.environ.get("SYNERGY_GITHUB_READ_TOKEN", "")
    try:
        provider = GitHubRestProvider(token=token)
    except LiveAuditAuthRequired as exc:
        print(json.dumps({
            "schema": "synergy.repository-live-audit-status/v1",
            "status": "AUTH_REQUIRED",
            "reason": str(exc),
            "required_scope": "read-only metadata access to all private/public Shtenco federation repositories",
        }, indent=2, sort_keys=True))
        return 2

    expected = load_expected_repositories(ROOT / "config/expected_repositories_v1.json")
    artifact = audit_repositories(expected, provider)
    print(json.dumps(artifact, indent=2, sort_keys=True))
    return 0 if artifact["audit_status"] == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
