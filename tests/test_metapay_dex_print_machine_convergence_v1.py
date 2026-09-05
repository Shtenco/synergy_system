from copy import deepcopy

import pytest

from verify.verify_metapay_dex_print_machine_convergence_v1 import load_policy, verify


def test_policy_verifies() -> None:
    verify(load_policy())


@pytest.mark.parametrize(
    "key",
    [
        "internal_mint_is_external_profit",
        "internal_burn_is_external_profit",
        "internal_revaluation_is_external_profit",
        "own_token_mcap_is_canonical_nav",
        "flash_principal_is_external_profit",
        "unused_authorization_capacity_is_profit",
        "capital_reallocation_creates_system_pnl",
        "dex_hard_tvl_equals_system_hard_nav",
        "issuance_cash_is_automatically_profit",
    ],
)
def test_cannot_relabel_internal_or_reallocated_value_as_profit(key: str) -> None:
    policy = deepcopy(load_policy())
    policy["economic_invariants"][key] = True
    with pytest.raises(AssertionError):
        verify(policy)


def test_usd_and_usdt_cannot_be_collapsed() -> None:
    policy = deepcopy(load_policy())
    policy["graph"]["usd_and_usdt_are_distinct_nodes"] = False
    with pytest.raises(AssertionError):
        verify(policy)


def test_synthetic_fx_reference_cannot_become_executable_edge() -> None:
    policy = deepcopy(load_policy())
    policy["graph"]["synthetic_fx_reference_is_not_executable_edge"] = False
    with pytest.raises(AssertionError):
        verify(policy)


def test_public_p2p_snapshot_cannot_be_execution_proof() -> None:
    policy = deepcopy(load_policy())
    policy["market_evidence_policy"]["public_p2p_snapshot_is_not_execution_proof"] = False
    with pytest.raises(AssertionError):
        verify(policy)


def test_print_machine_cannot_be_promoted_to_value_source() -> None:
    policy = deepcopy(load_policy())
    policy["print_machine_role"]["status"] = "AUTONOMOUS_VALUE_SOURCE"
    with pytest.raises(AssertionError):
        verify(policy)


def test_financial_os_remains_final_classifier() -> None:
    policy = deepcopy(load_policy())
    policy["external_profit_bus"]["canonical_owner"] = "Shtenco/synergy_pay_system"
    with pytest.raises(AssertionError):
        verify(policy)


def test_ai_payment_authority_cannot_escalate() -> None:
    policy = deepcopy(load_policy())
    policy["authority"]["ai_payment_authority"] = "EXECUTE"
    with pytest.raises(AssertionError):
        verify(policy)


def test_auto_merge_cannot_be_enabled() -> None:
    policy = deepcopy(load_policy())
    policy["authority"]["auto_merge"] = True
    with pytest.raises(AssertionError):
        verify(policy)
