from __future__ import annotations

from pathlib import Path

from synergy_system import load_expected_repositories, load_federation, validate_federation

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    federation = load_federation(ROOT / "config/repository_federation_v1.yaml")
    expected = load_expected_repositories(ROOT / "config/expected_repositories_v1.json")
    validate_federation(federation, expected)
    print(
        "FEDERATION_VALID "
        f"repos={len(federation['repositories'])} "
        f"authorities={len(federation['exclusive_authorities'])} "
        f"edges={len(federation['canonical_dependency_direction'])}"
    )


if __name__ == "__main__":
    main()
