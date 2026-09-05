from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "global_bank_fx_universe_v1_20260906.json"
SNAPSHOT = ROOT / "research" / "global_bank_fx_quotes_v1_20260906.json"

EXPECTED_CURRENCIES = {
    "USD", "EUR", "GBP", "CHF", "JPY", "CNY", "HKD", "SGD", "AED", "TRY",
    "RUB", "KZT", "UZS", "KGS", "TJS", "BYN", "GEL", "INR", "KRW", "THB",
}

ALLOWED_MODES = {
    "PUBLIC_CURRENT_TABLE",
    "PUBLIC_STALE_TABLE",
    "PUBLIC_REFERENCE_ONLY",
    "AUTHENTICATED_API",
    "AUTHENTICATED_APP_OR_TRADER",
    "ON_DEMAND_QUOTE",
    "CAPABILITY_ONLY",
    "NO_FRESH_PUBLIC_QUOTE_FOUND",
}

ALLOWED_REGIONS = {"CIS_CENTRAL_ASIA", "EUROPE", "ASIA"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_registry(registry: dict) -> None:
    assert registry["schema"] == "synergy.global-bank-fx-universe/v1"
    assert registry["status"] == "RESEARCH_REGISTRY_NOT_EXECUTION_PROOF"
    assert len(registry["currencies"]) == 20
    assert set(registry["currencies"]) == EXPECTED_CURRENCIES

    banks = registry["banks"]
    assert len(banks) == 50
    ids = [bank["id"] for bank in banks]
    assert len(ids) == len(set(ids))
    assert all(bank["region"] in ALLOWED_REGIONS for bank in banks)
    assert all(bank["quote_mode"] in ALLOWED_MODES for bank in banks)
    assert all(bank.get("rails") for bank in banks)
    assert all(bank.get("research_status") for bank in banks)

    region_counts = {
        region: sum(1 for bank in banks if bank["region"] == region)
        for region in ALLOWED_REGIONS
    }
    assert region_counts == {"CIS_CENTRAL_ASIA": 26, "EUROPE": 14, "ASIA": 10}

    authority = registry["authority"]
    assert authority["ai_payment_authority"] == "NONE"
    assert authority["ai_trading_authority"] == "NONE"
    assert authority["ai_signing_authority"] == "NONE"
    assert authority["merge_authority"] == "HUMAN_MAINTAINER_ONLY"
    assert authority["auto_merge"] is False


def verify_snapshot(snapshot: dict) -> None:
    assert snapshot["schema"] == "synergy.global-bank-fx-research-snapshot/v1"
    assert snapshot["status"] == "RESEARCH_EVIDENCE_NOT_EXECUTION_PROOF"
    assert snapshot["quotes"]
    assert snapshot["payment_rails"]
    assert snapshot["pricing_or_tariff_capabilities"]

    for quote in snapshot["quotes"]:
        assert quote["institution"]
        assert quote["country"]
        assert quote["base"]
        assert quote["rates"]
        assert quote["evidence_class"]
        assert quote["source"].startswith("https://")

    invariants = snapshot["invariants"]
    for key in (
        "bank_supports_currency_does_not_imply_current_price",
        "swift_is_not_fx_rate",
        "cips_is_not_fx_rate",
        "alipay_plus_is_not_generic_cny_to_crypto_exchange",
        "cash_or_card_rate_is_not_business_wire_rate",
        "stale_public_quote_is_not_live_executable",
        "public_quote_requires_account_eligibility_before_execution",
    ):
        assert invariants[key] is True, key


if __name__ == "__main__":
    registry = load(REGISTRY)
    snapshot = load(SNAPSHOT)
    verify_registry(registry)
    verify_snapshot(snapshot)
    print("GLOBAL_BANK_FX_UNIVERSE_V1_OK")
