from copy import deepcopy

import pytest

from verify.verify_global_bank_fx_universe_v1 import (
    REGISTRY,
    SNAPSHOT,
    load,
    verify_registry,
    verify_snapshot,
)


def test_registry_and_snapshot_verify() -> None:
    verify_registry(load(REGISTRY))
    verify_snapshot(load(SNAPSHOT))


def test_registry_must_have_exactly_fifty_banks() -> None:
    registry = load(REGISTRY)
    registry["banks"] = registry["banks"][:-1]
    with pytest.raises(AssertionError):
        verify_registry(registry)


def test_registry_must_have_exactly_twenty_currencies() -> None:
    registry = load(REGISTRY)
    registry["currencies"] = registry["currencies"][:-1]
    with pytest.raises(AssertionError):
        verify_registry(registry)


def test_capability_cannot_be_promoted_to_live_price_by_registry() -> None:
    registry = load(REGISTRY)
    registry["banks"][0]["quote_mode"] = "LIVE_EXECUTABLE"
    with pytest.raises(AssertionError):
        verify_registry(registry)


def test_swift_is_not_an_fx_price() -> None:
    snapshot = deepcopy(load(SNAPSHOT))
    snapshot["invariants"]["swift_is_not_fx_rate"] = False
    with pytest.raises(AssertionError):
        verify_snapshot(snapshot)


def test_alipay_plus_is_not_generic_crypto_fx() -> None:
    snapshot = deepcopy(load(SNAPSHOT))
    snapshot["invariants"]["alipay_plus_is_not_generic_cny_to_crypto_exchange"] = False
    with pytest.raises(AssertionError):
        verify_snapshot(snapshot)


def test_stale_quote_cannot_be_live_execution_evidence() -> None:
    snapshot = deepcopy(load(SNAPSHOT))
    snapshot["invariants"]["stale_public_quote_is_not_live_executable"] = False
    with pytest.raises(AssertionError):
        verify_snapshot(snapshot)


def test_ai_authority_cannot_escalate() -> None:
    registry = deepcopy(load(REGISTRY))
    registry["authority"]["ai_trading_authority"] = "EXECUTE"
    with pytest.raises(AssertionError):
        verify_registry(registry)


def test_auto_merge_cannot_be_enabled() -> None:
    registry = deepcopy(load(REGISTRY))
    registry["authority"]["auto_merge"] = True
    with pytest.raises(AssertionError):
        verify_registry(registry)
