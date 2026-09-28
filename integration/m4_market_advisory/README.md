# M4 Wave 1 — Market Advisory Federation

Первая волна расширения федерации после M2/M3.

## Scope

```text
MarketVision ───────────────┐
Adaptive Engine ───────────┤
Market Graph ──────────────┤
Market Maker ──────────────┤→ MIDAS advisory inputs
AI Investment Committee ───┘
```

Добавлены пять независимых typed contracts:

- `synergy.trading.market-features/v1`
- `synergy.trading.market-regime/v1`
- `synergy.trading.fair-value/v1`
- `synergy.trading.liquidity-quote/v1`
- `synergy.trading.investment-thesis/v1`

Все пять являются **advisory/data inputs**. Ни один payload не получает права исполнения сделки. MIDAS consumer сохраняет `authorization=false`, а committee veto не может быть преобразован в BUY/SELL.

## Promotion gate

```text
6 pinned repositories
→ 5 exact producer → MIDAS transfers
→ evidence bundle
→ verify_evidence.py
→ только после наблюдаемого PASS:
ADAPTER_IMPLEMENTED → E2E_TESTED
```

## Run

```bash
export SYNERGY_REPOS_ROOT=/path/to/sibling/checkouts
export SYNERGY_VERIFY_LOCK=1
python synergy_system/integration/m4_market_advisory/run.py
python synergy_system/integration/m4_market_advisory/verify_evidence.py
```

До успешного наблюдаемого запуска эти пять edge остаются `ADAPTER_IMPLEMENTED`.
