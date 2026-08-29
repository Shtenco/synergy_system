from __future__ import annotations

import argparse
import json
from pathlib import Path

from synergy_system.governance_lint_v3 import assert_patch_allowed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--patch-file", required=True)
    parser.add_argument("--policy", default="config/authority_lint_policy_v1.json")
    parser.add_argument("--expected", default="config/expected_repositories_v1.json")
    args = parser.parse_args()

    policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))
    expected = set(json.loads(Path(args.expected).read_text(encoding="utf-8"))["repositories"])
    patch = Path(args.patch_file).read_text(encoding="utf-8")
    assert_patch_allowed(
        repository=args.repository,
        path=args.path,
        patch=patch,
        policy=policy,
        expected_repositories=expected,
    )
    print("AUTHORITY_PATCH_ALLOWED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
