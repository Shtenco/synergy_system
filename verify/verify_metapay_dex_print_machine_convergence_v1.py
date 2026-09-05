from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "governance" / "metapay_dex_print_machine_convergence_v1.json"

REQUIRED_FALSE = {
    "internal_mint_is_external_profit",
    "internal_burn_is_external_profit",
    "internal_revaluation_is_external_profit",
    "own_token_mcap_is_canonical_nav",
    "flash_principal_is_external_profit",
    "unused_authorization_capacity_is_profit",
    "capital_reallocation_creates_system_pnl",
    "dex_hard_tvl_equals_system_hard_nav",
    "issuance_cash_is_automatically_profit",
}

REQUIRED_TRUE = {
    "external_profit_requires_realized_settlement",
    "external_profit_requires_principal_accounted",
    "external_profit_requires_flash_repayment_when_used",
    "external_profit_requires_explicit_costs_deducted",
    "external_profit_requires_independent_external_counterparty_evidence",
    "financial_os_is_final_economic_classifier",
}

REQUIRED_CLASSIFICATIONS = {
    "REALIZED_EXTERNAL_PNL",
    "EXTERNAL_INFLOW_REQUIRES_ACCOUNTING_CLASSIFICATION",
    "CAPITAL_REALLOCATION_PNL_ZERO",
    "INTERNAL_MARK_NOT_EXTERNAL_VALUE",
    "NOT_REALIZED",
    "NON_POSITIVE_EXTERNAL_PNL",
    "INADMISSIBLE",
}

REQUIRED_FORBIDDEN_CLAIMS = {
    "PERPETUAL_YIELD_FROM_MINT",
    "PROFIT_FROM_INTERNAL_MARK_ONLY",
    "PROFIT_FROM_MOVING_OWN_RESERVES",
    "SOLVENCY_FROM_UNBACKED_BRIDGE_REDEMPTION",
}


def load_policy(path: Path = POLICY_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify(policy: dict) -> None:
    assert policy["schema"] == "synergy.metapay-dex-print-machine-convergence/v1"
    assert policy["status"] == "RND_CANDIDATE_NOT_CANONICAL"
    assert policy["canonical_promotion"] is False

    repos = policy["repositories"]
    assert repos["canonical_accounting"] == "Shtenco/synergy_financial_os"
    assert repos["metapay_execution_and_evidence"] == "Shtenco/synergy_pay_system"
    assert repos["dex_finance_rnd"] == "Shtenco/ai_financial_system"
    assert repos["print_machine_rnd_placeholder"] == "Shtenco/print_money_synergychain"

    graph = policy["graph"]
    assert graph["usd_and_usdt_are_distinct_nodes"] is True
    assert graph["synthetic_fx_reference_is_not_executable_edge"] is True
    assert "USD" in graph["external_nodes"]
    assert "USDT" in graph["external_nodes"]
    assert "P2P" in graph["edge_kinds"]
    assert "DEX_SWAP" in graph["edge_kinds"]
    assert "INTERNAL_REVALUATION" in graph["edge_kinds"]

    invariants = policy["economic_invariants"]
    for key in REQUIRED_FALSE:
        assert invariants[key] is False, key
    for key in REQUIRED_TRUE:
        assert invariants[key] is True, key

    bus = policy["external_profit_bus"]
    assert bus["candidate_formula"] == (
        "settled_output - input_principal - external_costs - flash_premium"
    )
    assert set(bus["classifications"]) == REQUIRED_CLASSIFICATIONS
    assert bus["canonical_owner"] == "Shtenco/synergy_financial_os"

    press = policy["print_machine_role"]
    assert press["status"] == "RND_OPPORTUNITY_AMPLIFIER_NOT_VALUE_SOURCE"
    assert set(press["forbidden_claims"]) == REQUIRED_FORBIDDEN_CLAIMS
    assert press["allowed_sequence"][0] == "REALIZED_EXTERNAL_PNL_RECOGNIZED"
    assert press["allowed_sequence"][-1] == "NAV_AND_CAPACITY_RECOMPUTE"

    hard_tvl = policy["hard_tvl_rule"]
    assert hard_tvl["hard_tvl_growth_alone_is_system_profit"] is False

    market = policy["market_evidence_policy"]
    for key in (
        "quotes_are_ephemeral",
        "stale_quote_must_fail_closed",
        "jurisdiction_mismatch_must_fail_closed",
        "payment_method_mismatch_must_fail_closed",
        "limit_or_depth_mismatch_must_fail_closed",
        "public_p2p_snapshot_is_not_execution_proof",
    ):
        assert market[key] is True, key

    authority = policy["authority"]
    for key in (
        "ai_financial_authority",
        "ai_payment_authority",
        "ai_accounting_authority",
        "ai_signing_authority",
        "ai_blockchain_submission_authority",
        "ai_production_deployment_authority",
    ):
        assert authority[key] == "NONE", key
    assert authority["merge_authority"] == "HUMAN_MAINTAINER_ONLY"
    assert authority["auto_merge"] is False


if __name__ == "__main__":
    verify(load_policy())
    print("METAPAY_DEX_PRINT_MACHINE_CONVERGENCE_V1_OK")
