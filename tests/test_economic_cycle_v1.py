from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from synergy_system.economic_cycle_v1 import EconomicCycleV1Error, canonical_digest, verify_economic_cycle_v1

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"evidence/economic_os_e2e_cycle_v1.json"

def load():return json.loads(SOURCE.read_text())
def rehash(item):
    body=dict(item);body.pop("digest",None);item["digest"]=canonical_digest(body);return item

def test_canonical_economic_cycle_v1_verifies():
    item=verify_economic_cycle_v1(load())
    assert item["protocol_status"]=="E2E_PROTOCOL_DAG_CLOSED_NOT_LIVE_EXECUTED"
    assert item["live_execution_claim"] is False
    assert len(item["lifecycle"])==12

def test_fresh_hash_cannot_claim_live_execution():
    item=load();item["live_execution_claim"]=True;item["protocol_status"]="LIVE_EXECUTED";rehash(item)
    with pytest.raises(EconomicCycleV1Error):verify_economic_cycle_v1(item)

def test_fresh_hash_cannot_grant_ai_authority():
    item=load();item["ai_authority"]="AUTONOMOUS_TREASURY";rehash(item)
    with pytest.raises(EconomicCycleV1Error):verify_economic_cycle_v1(item)

def test_fresh_hash_cannot_swap_financial_os_head():
    item=load();item["repository_bindings"]["financial_os"]["available_capacity_v4_commit"]="0"*40;rehash(item)
    with pytest.raises(EconomicCycleV1Error):verify_economic_cycle_v1(item)

def test_fresh_hash_cannot_move_accounting_to_metapay():
    item=load();item["accounting_authority"]="Shtenco/synergy_pay_system";rehash(item)
    with pytest.raises(EconomicCycleV1Error):verify_economic_cycle_v1(item)

def test_fresh_hash_cannot_remove_live_execution_blocker():
    item=load();item["blockers"].remove("ONE_LIVE_EXTERNAL_VALUE_TO_NEXT_CAPACITY_EXECUTION_NOT_CAPTURED");rehash(item)
    with pytest.raises(EconomicCycleV1Error):verify_economic_cycle_v1(item)

def test_reference_vectors_reconcile_but_are_not_one_live_fixture():
    item=verify_economic_cycle_v1(load());vectors=item["reference_vectors"]
    assert vectors["external_revenue_lineage"]["settled_external_amount"]=="125"
    assert vectors["distribution_reversal_lineage"]["restored_remaining_entitlement"]=="23.9"
    assert vectors["cross_vector_execution_status"]=="PROTOCOL_LINKED_NOT_ONE_LIVE_RUNTIME_FIXTURE"
