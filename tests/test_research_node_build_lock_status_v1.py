from pathlib import Path


def test_source_candidate_status_note_is_fail_closed() -> None:
    text = (Path(__file__).resolve().parents[1] / "docs/RESEARCH_NODE_BUILD_LOCK_STATUS_20260821.md").read_text()
    assert "SOURCE_CANDIDATE_NOT_BUILD_VERIFIED" in text
    assert "build_artifact_digest` is intentionally `null" in text
    assert "no Meta-OS service may become runnable" in text
    assert "not a deployable build attestation" in text
