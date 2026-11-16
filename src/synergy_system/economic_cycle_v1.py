from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Any, Mapping

SCHEMA="synergy.economic-cycle/v1"
EXPECTED_DIGEST="83f9c3ee0c168ca50212ebaa1e64c58c08eb87fd040a8b5f214ee4987242f3f1"
EXPECTED_FINANCIAL_COMMITS={
    "external_revenue_lineage_commit":"a09213bca4f8282dc63bc359f3b94e94773b0ddb",
    "ledger_close_trace_v6_commit":"8727b2ff44d1425d84f37c051fc67c083534f4b7",
    "budget_state_v2_commit":"7034ebe6413f15a550d91e882339a178af237bf4",
    "available_capacity_v3_commit":"17fbac0f45b1c0835f113a2a45cda9522858e8b5",
    "handoff_v3_commit":"08ad477bd8ad6551f842763e8ae8b6aa2b549bae",
    "fee_accounting_v3_commit":"6ad688fe6fd2fc41fe59ada97a6f560a0eed3d0b",
    "reversal_accounting_v2_commit":"73b2560455d765c9c143b5af8d099cad45343746",
    "budget_state_v3_commit":"753ed935ca704626e3ebdfa79a898d34f58d3732",
    "available_capacity_v4_commit":"d21ce6b5bd91422c45f938b2d4ec641974106944",
}
EXPECTED_METAPAY_COMMITS={
    "settlement_v3_commit":"8bda0d9853af905cd043b94b12f0b62bac58a1d6",
    "reversal_v2_commit":"a4b7b2876915e7f70089947a5b40f3cff81458d9",
}
EXPECTED_LIFECYCLE=(
    (1,"EXTERNAL_VALUE_EVIDENCE","Shtenco/synergy_pay_system","settlement.receipt/v2"),
    (2,"REVENUE_RECOGNITION","Shtenco/synergy_financial_os","revenue.recognition/v2"),
    (3,"CANONICAL_LEDGER_AND_CLOSE","Shtenco/synergy_financial_os","economic.cycle-trace/v6"),
    (4,"FEE_AWARE_DISTRIBUTION_ENTITLEMENT","Shtenco/synergy_financial_os","distribution.budget-state/v2"),
    (5,"CURRENT_DISTRIBUTION_CAPACITY","Shtenco/synergy_financial_os","distribution.available-capacity/v3"),
    (6,"HUMAN_GOVERNANCE_HANDOFF","Shtenco/synergy_financial_os","distribution.execution-ticket/v3"),
    (7,"METAPAY_SETTLEMENT","Shtenco/synergy_pay_system","distribution.utilization/v3"),
    (8,"SETTLEMENT_ACCOUNTING","Shtenco/synergy_financial_os","distribution.fee-accounting-decision/v3"),
    (9,"LATER_SETTLEMENT_REVERSAL","Shtenco/synergy_pay_system","distribution.settlement-reversal/v2"),
    (10,"REVERSAL_ACCOUNTING","Shtenco/synergy_financial_os","distribution.reversal-accounting-decision/v2"),
    (11,"ENTITLEMENT_RESTORATION","Shtenco/synergy_financial_os","distribution.budget-state/v3"),
    (12,"NEXT_CYCLE_CAPACITY","Shtenco/synergy_financial_os","distribution.available-capacity/v4"),
)
EXPECTED_BLOCKERS={
    "STACKED_PR_CHAIN_NOT_CANONICALLY_MERGED",
    "ONE_LIVE_EXTERNAL_VALUE_TO_NEXT_CAPACITY_EXECUTION_NOT_CAPTURED",
    "ECONOMIC_BLOCKCHAIN_COMMITMENT_NOT_CREATED",
    "ECONOMIC_TESTNET_NOT_EXECUTED",
}

class EconomicCycleV1Error(ValueError):pass

def canonical_digest(payload:Mapping[str,Any])->str:
    return hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")).hexdigest()

def verify_economic_cycle_v1(payload:Mapping[str,Any])->dict[str,Any]:
    if not isinstance(payload,Mapping) or payload.get("schema")!=SCHEMA:raise EconomicCycleV1Error("unsupported economic cycle schema")
    item=dict(payload);supplied=item.pop("digest",None)
    if supplied!=canonical_digest(item) or supplied!=EXPECTED_DIGEST:raise EconomicCycleV1Error("economic cycle digest mismatch")
    if item.get("authority")!="SYNERGY_SYSTEM_PROVENANCE_ONLY":raise EconomicCycleV1Error("system manifest authority mismatch")
    if item.get("accounting_authority")!="Shtenco/synergy_financial_os" or item.get("settlement_authority")!="Shtenco/synergy_pay_system":raise EconomicCycleV1Error("domain authority mismatch")
    if item.get("governance_authority")!="HUMAN_COMMITTEE_OR_MULTISIG_ONLY":raise EconomicCycleV1Error("governance must remain human/multisig")
    if item.get("ai_authority")!="NONE" or item.get("execution_authority")!="NONE" or item.get("blockchain_submission_authority")!="NONE":raise EconomicCycleV1Error("federation manifest cannot execute or delegate authority")
    if item.get("protocol_status")!="E2E_PROTOCOL_DAG_CLOSED_NOT_LIVE_EXECUTED" or item.get("canonical_merge_status")!="STACKED_PR_CANDIDATE_NOT_MERGED" or item.get("live_execution_claim") is not False:raise EconomicCycleV1Error("protocol/live status escalation")
    if item.get("trust_finalization")!="EXTERNAL_COMMITMENT_REQUIRED":raise EconomicCycleV1Error("trust finalization boundary mismatch")
    bindings=item.get("repository_bindings")
    if not isinstance(bindings,Mapping):raise EconomicCycleV1Error("repository bindings missing")
    financial=bindings.get("financial_os");metapay=bindings.get("metapay");system=bindings.get("system")
    if not isinstance(financial,Mapping) or financial.get("repository")!="Shtenco/synergy_financial_os":raise EconomicCycleV1Error("Financial OS binding missing")
    if not isinstance(metapay,Mapping) or metapay.get("repository")!="Shtenco/synergy_pay_system":raise EconomicCycleV1Error("MetaPay binding missing")
    for field,value in EXPECTED_FINANCIAL_COMMITS.items():
        if financial.get(field)!=value:raise EconomicCycleV1Error(f"Financial OS commit drift: {field}")
    for field,value in EXPECTED_METAPAY_COMMITS.items():
        if metapay.get(field)!=value:raise EconomicCycleV1Error(f"MetaPay commit drift: {field}")
    if not isinstance(system,Mapping) or system.get("compute_preproduction_rc5_root")!="0dd56320df6a1e18a7f77470b0609f55cb9c134ac67bbedeebdd3600e724124b":raise EconomicCycleV1Error("Compute preproduction root drift")
    phases=item.get("lifecycle")
    if not isinstance(phases,list) or len(phases)!=len(EXPECTED_LIFECYCLE):raise EconomicCycleV1Error("lifecycle cardinality mismatch")
    observed=[]
    for phase in phases:
        if not isinstance(phase,Mapping) or phase.get("required") is not True:raise EconomicCycleV1Error("all v1 lifecycle phases are required")
        observed.append((phase.get("ordinal"),phase.get("phase"),phase.get("owner"),phase.get("schema")))
    if tuple(observed)!=EXPECTED_LIFECYCLE:raise EconomicCycleV1Error("lifecycle order/ownership/schema drift")
    inv=item.get("economic_invariants")
    if not isinstance(inv,Mapping):raise EconomicCycleV1Error("economic invariants missing")
    if inv.get("internal_mint_or_revaluation_is_profit") is not False or inv.get("distribution_principal_is_realized_pnl") is not False or inv.get("beneficiary_principal_can_be_reduced_by_fee") is not False or inv.get("reversal_authorization_reactivated") is not False:raise EconomicCycleV1Error("economic invariant escalation")
    if inv.get("settlement_fee_pnl_effect")!="-ACTUAL_EXTERNAL_FEE" or inv.get("fee_refund_pnl_effect")!="+REFUNDED_ORIGINAL_FEE" or inv.get("reversal_processing_fee_pnl_effect")!="-REVERSAL_PROCESSING_FEE":raise EconomicCycleV1Error("fee P&L invariant drift")
    vectors=item.get("reference_vectors")
    if not isinstance(vectors,Mapping) or vectors.get("cross_vector_execution_status")!="PROTOCOL_LINKED_NOT_ONE_LIVE_RUNTIME_FIXTURE":raise EconomicCycleV1Error("reference execution status escalation")
    revenue=vectors.get("external_revenue_lineage");dist=vectors.get("distribution_reversal_lineage")
    if not isinstance(revenue,Mapping) or Decimal(revenue["settled_external_amount"])!=Decimal(revenue["recognized_external_revenue"])+Decimal(revenue["tax_liability"])+Decimal(revenue["refund_reserve"]):raise EconomicCycleV1Error("external revenue vector does not reconcile")
    if not isinstance(dist,Mapping):raise EconomicCycleV1Error("distribution vector missing")
    net_fee=Decimal(dist["post_close_settlement_fee"])-Decimal(dist["refunded_original_fee"])+Decimal(dist["reversal_processing_fee"])
    restored=Decimal(dist["gross_period_profit_budget"])-net_fee-(Decimal(dist["principal_distribution"])-Decimal(dist["principal_return"]))
    if restored!=Decimal(dist["restored_remaining_entitlement"]):raise EconomicCycleV1Error("restored entitlement vector mismatch")
    if Decimal(dist["next_cycle_liquidity_limited_capacity"])>restored:raise EconomicCycleV1Error("next capacity exceeds restored entitlement")
    blockers=item.get("blockers")
    if not isinstance(blockers,list) or set(blockers)!=EXPECTED_BLOCKERS or len(blockers)!=len(EXPECTED_BLOCKERS):raise EconomicCycleV1Error("release blockers drift")
    item["digest"]=supplied
    return item
