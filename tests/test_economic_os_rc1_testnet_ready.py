from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "economic_os_rc1_verifier", ROOT / "verify" / "verify_economic_os_rc1_testnet_ready.py"
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MOD)


def load():
    return json.loads((ROOT / "releases" / "economic_os_rc1_testnet_ready_20260828.json").read_text(encoding="utf-8"))


def rehash(item):
    body = dict(item); body.pop("digest", None)
    item["digest"] = hashlib.sha256(
        json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return item


def test_rc1_passes():
    assert MOD.verify(load()) == MOD.EXPECTED_DIGEST


@pytest.mark.parametrize("field,value", [
    ("economic_cycle_digest", "0" * 64),
    ("economic_commitment_digest", "1" * 64),
    ("testnet_genesis_digest", "2" * 64),
    ("protocol_status", "LIVE_EXECUTED"),
    ("economic_blockchain_commitment_status", "SUBMITTED"),
    ("economic_testnet_status", "EXECUTED"),
    ("canonical_merge_status", "MERGED"),
    ("live_execution_claim", True),
    ("signing_authority", "AI"),
    ("accounting_authority", "AI"),
    ("payment_authority", "AI"),
])
def test_fresh_hash_cannot_promote_state_or_authority(field, value):
    item = load(); item[field] = value; rehash(item)
    with pytest.raises(MOD.EconomicOSRC1Error):
        MOD.verify(item)


def test_fresh_hash_cannot_remove_live_execution_blocker():
    item = load()
    item["blockers"] = [x for x in item["blockers"] if x != "ONE_LIVE_EXTERNAL_VALUE_TO_NEXT_CAPACITY_EXECUTION_NOT_CAPTURED"]
    rehash(item)
    # RC1 is an immutable release root. A fresh hash of mutated blocker content
    # is rejected at the stronger pinned-root boundary before semantic blocker checks.
    with pytest.raises(MOD.EconomicOSRC1Error, match="release digest mismatch"):
        MOD.verify(item)
