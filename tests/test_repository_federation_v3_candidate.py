from __future__ import annotations
import copy, hashlib, json, sys
from pathlib import Path
import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "verify"))
from verify_repository_federation_v3_candidate import verify

CANDIDATE = json.loads((ROOT / "registry/repository_federation_v3_candidate_20260905.json").read_text())
AUDIT = json.loads((ROOT / "registry/repository_evidence_audit_v1_20260905.json").read_text())
SCHEMA = json.loads((ROOT / "schemas/repository_federation_v3_candidate.schema.json").read_text())

def rehash(obj, key):
    x = dict(obj); x.pop(key, None)
    obj[key] = hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    return obj

def test_canonical_candidate_and_audit_pass():
    Draft202012Validator(SCHEMA).validate(CANDIDATE)
    verify(CANDIDATE, AUDIT)

def test_missing_post_v2_repo_rejected_after_fresh_hash():
    c = copy.deepcopy(CANDIDATE)
    c["combined_repository_names"].remove("Shtenco/synergy_metachain")
    c["repository_count"] = 44
    rehash(c, "federation_candidate_digest")
    with pytest.raises(ValueError): verify(c, AUDIT)

def test_hidden_extra_repo_rejected_after_fresh_hash():
    c = copy.deepcopy(CANDIDATE)
    c["combined_repository_names"].append("Shtenco/hidden_repo")
    c["repository_count"] = 46
    rehash(c, "federation_candidate_digest")
    with pytest.raises(ValueError): verify(c, AUDIT)

def test_canonical_self_promotion_rejected_after_fresh_hash():
    c = copy.deepcopy(CANDIDATE); c["canonical_promotion"] = True
    rehash(c, "federation_candidate_digest")
    with pytest.raises(ValueError): verify(c, AUDIT)

def test_ai_authority_escalation_rejected_after_fresh_hash():
    c = copy.deepcopy(CANDIDATE); c["policy"]["ai_payment_authority"] = "LIVE"
    rehash(c, "federation_candidate_digest")
    with pytest.raises(ValueError): verify(c, AUDIT)

def test_internal_revaluation_profit_rejected_after_fresh_hash():
    c = copy.deepcopy(CANDIDATE); c["policy"]["internal_mint_or_revaluation_is_external_profit"] = True
    rehash(c, "federation_candidate_digest")
    with pytest.raises(ValueError): verify(c, AUDIT)

@pytest.mark.parametrize("repo", ["Shtenco/turbo_linux", "Shtenco/cashero", "Shtenco/usds"])
def test_known_security_finding_cannot_be_erased(repo):
    a = copy.deepcopy(AUDIT)
    next(x for x in a["records"] if x["repository"] == repo)["secret_hygiene"] = "NO_ROOT_SECRET_FILENAME_OBSERVED_NOT_EXHAUSTIVE"
    rehash(a, "audit_digest")
    c = copy.deepcopy(CANDIDATE); c["evidence_audit"]["audit_digest"] = a["audit_digest"]
    rehash(c, "federation_candidate_digest")
    with pytest.raises(ValueError): verify(c, a)

def test_audit_membership_drift_rejected_after_fresh_hash():
    a = copy.deepcopy(AUDIT); a["records"][0]["repository"] = "Shtenco/other"
    rehash(a, "audit_digest")
    c = copy.deepcopy(CANDIDATE); c["evidence_audit"]["audit_digest"] = a["audit_digest"]
    rehash(c, "federation_candidate_digest")
    with pytest.raises(ValueError): verify(c, a)

def test_duplicate_repository_rejected():
    c = copy.deepcopy(CANDIDATE); c["combined_repository_names"][-1] = c["combined_repository_names"][0]
    rehash(c, "federation_candidate_digest")
    with pytest.raises(ValueError): verify(c, AUDIT)

def test_parent_v2_root_tamper_rejected():
    c = copy.deepcopy(CANDIDATE); c["parent"]["federation_digest"] = "0" * 64
    rehash(c, "federation_candidate_digest")
    with pytest.raises(ValueError): verify(c, AUDIT)

def test_invalid_roadmap_step_rejected():
    c = copy.deepcopy(CANDIDATE); c["post_v2_additions"][0]["top20_steps"] = [21]
    rehash(c, "federation_candidate_digest")
    with pytest.raises(ValueError): verify(c, AUDIT)

def test_digest_tamper_rejected():
    c = copy.deepcopy(CANDIDATE); c["federation_candidate_digest"] = "0" * 64
    with pytest.raises(ValueError): verify(c, AUDIT)

def test_hidden_candidate_field_rejected_even_with_fresh_hash():
    c = copy.deepcopy(CANDIDATE); c["live_verified"] = True
    rehash(c, "federation_candidate_digest")
    with pytest.raises(ValueError): verify(c, AUDIT)
