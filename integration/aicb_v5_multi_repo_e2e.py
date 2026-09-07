#!/usr/bin/env python3
"""Literal native-class E2E for SYNERGY AICB V5.

This script is intentionally repository-path based: it imports the actual AICB
policy class from ai_financial_system, ProductiveGrowthAttestation from
synergy_eurasian and Financial OS accounting contracts from
synergy_financial_os. It does not vendor or reimplement those domain classes.

It proves the off-chain evidence chain only. The Solidity dual-gate enforcement
is tested separately by ProductiveMonetaryEscrowV2 Hardhat tests.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def add_import_roots(aicb_root: Path, eurasian_root: Path, financial_root: Path) -> None:
    sys.path.insert(0, str(aicb_root.resolve()))
    sys.path.insert(0, str((eurasian_root / "src").resolve()))
    sys.path.insert(0, str((financial_root / "src").resolve()))


def run(aicb_root: Path, eurasian_root: Path, financial_root: Path) -> dict:
    add_import_roots(aicb_root, eurasian_root, financial_root)

    from ai_centrobank.productive_v5_policy import AICBPolicyV5, EconomicSnapshotV5
    from synergy_eurasian import ProductiveGrowthAttestation
    from synergy_financial_os import EligibleAssetGrowthAttestation, EmissionReleaseRecognition

    snapshot = EconomicSnapshotV5(
        period_id="sandbox-e2e-001",
        monthly_inflation=0.004,
        target_monthly_inflation=0.004,
        inflation_tolerance=0.010,
        reserve_cover=0.45,
        min_reserve_cover=0.22,
        target_reserve_cover=0.45,
        goods_growth=0.010,
        capacity_growth=0.010,
        employment_rate=0.95,
        money_to_goods=1.00,
        target_money_to_goods=1.05,
        available_matching_capital=85.0,
        required_match_ratio=0.85,
        max_period_emission=100.0,
        physical_consistency_gap=0.0,
        supply_accounting_gap=0.0,
    )
    proposal = AICBPolicyV5.evaluate(snapshot)
    assert not proposal.blocked
    assert 0 < proposal.requested_emission <= 100.0

    productive = ProductiveGrowthAttestation(
        close_id="productive-close-001",
        close_sequence=1,
        project_ids=("factory-sandbox-001",),
        goods_output_growth_units=100.0,
        capacity_growth_units=20.0,
        verified_goods_value_growth=35.0,
        verified_capacity_value_growth=15.0,
        fraud_or_quality_haircut_value=10.0,
        physical_consistency_gap=0.0,
        valuation_method_ref="valuation:sandbox-independent-v1",
        evidence_refs=("warehouse:acceptance:001", "equipment:commissioning:001"),
    )
    assert productive.credited_productive_growth == 40.0

    financial = EligibleAssetGrowthAttestation(
        close_id="financial-close-002",
        close_sequence=2,
        previous_hardnav=1000.0,
        current_hardnav=1050.0,
        previous_liabilities=100.0,
        current_liabilities=100.0,
        eligible_asset_gross_growth=50.0,
        internal_mark_change=0.0,
        flash_principal_inflow=0.0,
        eligible_asset_classes=("VERIFIED_PRODUCTIVE_ASSET",),
        evidence_refs=("financial:ledger:sandbox-002",),
    )
    assert financial.credited_growth == 50.0

    coverage_ratio = 2.0
    approved_units = proposal.requested_emission
    required_growth = approved_units * coverage_ratio
    dual_credit = min(productive.credited_productive_growth, financial.credited_growth)
    released_units = approved_units * dual_credit / required_growth

    # With 200% coverage, 40 of weaker dual evidence unlocks 20 monetary units,
    # regardless of the bounded policy proposal size.
    assert dual_credit == 40.0
    assert abs(released_units - 20.0) < 1e-12
    assert released_units * coverage_ratio <= productive.credited_productive_growth
    assert released_units * coverage_ratio <= financial.credited_growth

    recognition = EmissionReleaseRecognition(
        proposal_id="proposal:sandbox-e2e-001",
        release_tx_ref="sandbox:hardhat:release-001",
        financial_growth_attestation_ref=financial.close_id,
        productive_growth_attestation_ref=productive.close_id,
        released_units=released_units,
        unit_value=1.0,
        accounting_classification="MONETARY_LIABILITY",
    )
    assert recognition.recognized_revenue == 0.0
    assert recognition.recognized_profit == 0.0

    return {
        "status": "PASS_REFERENCE_MULTI_REPO_NATIVE_CLASSES",
        "scope": "OFFCHAIN_NATIVE_CLASS_INTEGRATION_PLUS_SEPARATE_HARDHAT_GATE",
        "proposal": proposal.as_payload(),
        "productive": productive.as_payload(),
        "financial": financial.as_payload(),
        "dual_gate": {
            "coverage_ratio": coverage_ratio,
            "required_growth": required_growth,
            "productive_credit": productive.credited_productive_growth,
            "financial_credit": financial.credited_growth,
            "consumed_dual_credit": dual_credit,
            "released_units": released_units,
        },
        "recognition": recognition.as_payload(),
        "claims": {
            "live_economy_test": False,
            "live_chain_release": False,
            "macroeconomic_performance_proven": False,
            "mint_is_profit": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aicb-root", type=Path, required=True)
    parser.add_argument("--eurasian-root", type=Path, required=True)
    parser.add_argument("--financial-root", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    result = run(args.aicb_root, args.eurasian_root, args.financial_root)
    text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
