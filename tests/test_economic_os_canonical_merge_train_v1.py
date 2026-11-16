from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("merge_train", ROOT / "verify" / "verify_economic_os_canonical_merge_train_v1.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MOD)


def load():
    return json.loads((ROOT / "release_trains" / "economic_os_canonical_merge_train_v1.json").read_text(encoding="utf-8"))


def rehash(item):
    body = dict(item); body.pop("digest", None)
    item["digest"] = hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return item


def test_current_blocked_train_passes():
    assert MOD.verify(load()) == MOD.EXPECTED_DIGEST


def test_fresh_hash_cannot_remove_ci_gate():
    item = load(); item["current_gate"] = "READY_TO_MERGE"; rehash(item)
    with pytest.raises(MOD.MergeTrainV1Error): MOD.verify(item)


def test_fresh_hash_cannot_enable_ai_or_auto_merge():
    item = load(); item["auto_merge"] = True; item["ai_merge_authority"] = "AUTOPILOT"; rehash(item)
    with pytest.raises(MOD.MergeTrainV1Error): MOD.verify(item)


def test_fresh_hash_cannot_relabel_null_steps_as_pass():
    item = load(); item["observed_ci_evidence"][0]["classification"] = "EXECUTED_PASS"; rehash(item)
    with pytest.raises(MOD.MergeTrainV1Error): MOD.verify(item)


def test_pr_order_is_immutable_in_this_generation():
    item = load(); item["financial_os_lane"]["ordered_prs"] = list(reversed(item["financial_os_lane"]["ordered_prs"])); rehash(item)
    with pytest.raises(MOD.MergeTrainV1Error): MOD.verify(item)
