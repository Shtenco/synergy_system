from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "registry" / "global_currency_universe_v2_20260906.json"

BIS_TOP20 = (
    "USD", "EUR", "JPY", "GBP", "CNY", "CHF", "AUD", "CAD", "HKD", "SGD",
    "INR", "KRW", "SEK", "MXN", "NZD", "NOK", "TWD", "BRL", "ZAR", "PLN",
)
REGIONAL = ("RUB", "KZT", "UZS", "KGS", "TJS", "BYN", "GEL", "AED", "TRY", "THB")


def load() -> dict:
    return json.loads(PATH.read_text(encoding="utf-8"))


def verify(payload: dict) -> None:
    assert payload["schema"] == "synergy.global-currency-universe/v2"
    assert payload["status"] == "RESEARCH_UNIVERSE_NOT_EXECUTION_PROOF"

    top = payload["global_top20"]
    assert len(top) == 20
    assert tuple(item["currency"] for item in top) == BIS_TOP20
    assert tuple(item["rank"] for item in top) == tuple(range(1, 21))

    regional = payload["regional_strategic_extension"]
    assert tuple(item["currency"] for item in regional) == REGIONAL
    assert not set(BIS_TOP20).intersection(REGIONAL)

    effective = payload["effective_fiat_graph_assets"]
    assert len(effective) == 30
    assert len(effective) == len(set(effective))
    assert set(effective) == set(BIS_TOP20) | set(REGIONAL)

    crypto = payload["crypto_graph_assets_initial"]
    assert {"USDT", "USDC", "BTC", "ETH"}.issubset(crypto)
    assert not set(effective).intersection(crypto)

    inv = payload["invariants"]
    for key in (
        "global_top20_is_bis_ranked",
        "regional_extension_does_not_relabel_itself_as_global_top20",
        "fiat_and_stablecoin_assets_are_distinct_nodes",
        "registry_membership_is_not_executable_quote",
    ):
        assert inv[key] is True, key


if __name__ == "__main__":
    verify(load())
    print("GLOBAL_CURRENCY_UNIVERSE_V2_OK")
