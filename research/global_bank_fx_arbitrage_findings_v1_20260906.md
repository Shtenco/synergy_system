# Global Bank FX × Payment Rails × MetaPay Arbitrage Research v1

Date: 2026-09-06  
Target price date: 2026-09-05, with latest previous business-day quote where the target date is unavailable.  
Status: research evidence, **not execution proof**.

## Scope correction

The bank universe contains 50 institutional nodes across CIS/Central Asia/Georgia, Europe and Asia.

The currency universe is now split correctly into two layers.

### BIS 2025 global FX Top-20

By OTC FX turnover in the BIS 2025 Triennial Survey:

`USD EUR JPY GBP CNY CHF AUD CAD HKD SGD INR KRW SEK MXN NZD NOK TWD BRL ZAR PLN`

The first engineering pass had used a regionally optimized 20-currency set and therefore incorrectly called currencies such as KGS/TJS/BYN/GEL part of the global Top-20. That terminology is superseded by `registry/global_currency_universe_v2_20260906.json`.

### Regional Strategic Extension

For the actual SYNERGY geography and payment graph we add:

`RUB KZT UZS KGS TJS BYN GEL AED TRY THB`

Therefore the effective fiat research graph contains **30 currencies**.

Initial crypto extension:

`USDT USDC BTC ETH SOL BNB XRP TON`

Fiat, stablecoins and crypto assets remain distinct states.

## 50-bank selection

This is an engineering research universe, not a formal ranking of banks by assets. Banks were selected for cross-border FX/payment importance, regional relevance, API/public quote accessibility and settlement-rail usefulness.

Regional composition:

- CIS/Central Asia/Georgia: 26;
- Europe: 14;
- Asia: 10.

Machine-readable registry:

`registry/global_bank_fx_universe_v1_20260906.json`

Currency universe:

`registry/global_currency_universe_v2_20260906.json`

## Critical research result: a 50-bank × 20-currency live public matrix does not exist

Banks expose FX prices through materially different surfaces:

1. fresh public bid/ask tables;
2. stale/delayed public tables;
3. authenticated APIs;
4. authenticated apps/dealing platforms;
5. on-demand dealer/relationship-manager quotes;
6. rail/currency capability documents without an executable price.

Therefore registry presence never creates a priced graph edge.

The project stores separately:

- bank/currency/rail capability;
- public quote evidence;
- authenticated-quote requirement;
- actual executable evidence when available later.

## Strong public/current quote hubs found

### Bank CenterCredit — Kazakhstan

Fresh 2026-09-05 public KZT and cross-rate table includes USD, EUR, RUB, GBP, CNY, AED, CHF, TRY, UZS, JPY.

Important direct cross pairs:

- EUR/USD 1.16034 / 1.16168;
- USD/RUB 85.5 / 86.15;
- USD/CNY 6.7021 / 6.7153;
- CNY/RUB 12.6838 / 12.8948;
- USD/AED 3.6674 / 3.6786;
- USD/JPY 156.055 / 156.459;
- USD/CHF 0.808 / 0.812.

This makes BCC one of the strongest public research hubs, but public price still does not prove business account eligibility.

### Optima Bank — Kyrgyzstan

2026-09-05 non-cash rates explicitly applicable to legal entities/IP up to USD 10,000 equivalent:

- USD/KGS 87.40 / 87.80;
- EUR/KGS 101.20 / 102.20;
- KZT/KGS 0.185 / 0.200;
- RUB/KGS 0.990 / 1.040;
- CNY/KGS 12.25 / 13.75.

Above the threshold a negotiated Treasury rate is required.

### MBANK — Kyrgyzstan

2026-09-04 non-cash:

- USD/KGS 87.45 / 87.50;
- EUR/KGS 101.40 / 102.40;
- RUB/KGS 0.986 / 1.035;
- KZT/KGS 0.182 / 0.197.

Promotional SWIFT through 2026-09-30:

- USD: 0.2%, min USD35, max USD300;
- CNY: 0.2%, min CNY50, max CNY1000.

### Kapitalbank — Uzbekistan

2026-09-05 legal-entity/IP table:

- USD/UZS 11,759.62 / 11,830.39;
- EUR/UZS 13,562 / 13,835.71;
- RUB/UZS 129.01 / 137.43.

### Bank Eskhata — Tajikistan

2026-09-04 public conversion page includes USD/EUR/RUB and a broader block containing CNY/KZT/AED/TRY. The exact individual/legal-entity subsection must be bound before live use.

### Bank of China — China

2026-09-05 public BOC table creates a strong CNY hub including USD/EUR/GBP/CHF/JPY/HKD/SGD/AED/THB/TRY/KRW and directly RUB/KZT.

Normalized examples:

- USD→CNY bank-buy side: 6.7013 CNY/USD;
- client buy USD: 6.7295 CNY/USD;
- RUB→CNY: 0.0753 CNY/RUB;
- CNY→RUB: 12.6262626 RUB/CNY from the bank-sell RUB side;
- KZT→CNY: 0.0144 CNY/KZT;
- CNY→KZT: 66.6666667 KZT/CNY from the bank-sell KZT side.

### SMBC — Japan

2026-09-05 public internet-FX/deposit quotes:

- USD/JPY TTB/TTS 155.77 / 156.27;
- EUR/JPY 180.76 / 181.46;
- GBP/JPY 209.21 / 211.21;
- CHF/JPY 192.46 / 192.91.

These are research prices, not automatically corporate SWIFT prices.

### MUFG — Japan

Latest previous business day 2026-09-04:

- USD/JPY 154.68 / 156.68;
- EUR/JPY 179.57 / 182.57;
- GBP/JPY 206.68 / 214.68;
- CHF/JPY 191.82 / 193.62.

## Authenticated/API FX hubs

### TBC Bank — Georgia

Production API supports commercial rates and cross-conversion quotes with a developer API key.

### Bank of Georgia

Business API documentation exposes commercial/cross rates and conversion-order creation. Final authorization remains with the account/operator.

### Eurasian Bank — Kazakhstan

Smart Business provides authenticated real-time FX, multiple pairs and no separate conversion commission.

### Deutsche Bank FX4Cash

Real-time FX conversion integrated with international payments across a broad global currency set.

### Commerzbank FX Live Trader

Authenticated corporate real-time prices for more than 100 currency pairs.

### DBS FX Online

Authenticated live transparent pricing on 40+ pairs; broader FX capability covers 130+ currencies; telegraphic transfers support 33 currencies.

### UOB Business

Business telegraphic transfers support real-time FX locking and multi-currency payments.

### Ipak Yuli — Uzbekistan

Legal-entity dealing supports USD, EUR, GBP, CHF, JPY and RUB hard-currency cross-conversion. No separate fee is debited; pricing compensation is embedded in the dealer rate. Exact rate is on demand.

## Payment rails are graph edges, not FX prices

### SWIFT

SWIFT is a cross-border messaging/payment framework, not a universal exchange-rate feed.

Every SWIFT edge must bind:

- sender account/bank;
- recipient account/bank;
- currency;
- OUR/SHA/BEN or equivalent fee semantics;
- correspondent/intermediary fees;
- cut-off;
- settlement delay;
- exact bank FX quote if conversion occurs.

### CIPS

CIPS is an RMB settlement rail, not an FX price. It is valuable because it connects CNY settlement across regions. As of June 2026 CIPS reported 210 direct and 1,619 indirect participants.

### Alipay+

Alipay+ is modeled as merchant acquiring/payment/settlement infrastructure, **not as a generic treasury CNY↔crypto exchange**.

When transaction and settlement currencies differ, Alipay+ API/reporting documentation binds the transaction to a settlement quote. That authenticated payment quote may become a real payment edge. Settlement reports are reconciliation evidence rather than an independent market quote.

### UnionPay

UnionPay publishes a card-network composite reference rate. Issuer fees are excluded and transaction-date or settlement-date rates may apply. This is not equivalent to a corporate dealing/SWIFT price.

## Cross-bank sanity tests — before transfer costs

No positive arbitrage was proved in the first high-quality public bank comparisons.

| Cycle | Gross return before transfer cost |
| --- | ---: |
| CNY→USD @ BCC → CNY @ BOC | -0.2085% |
| CNY→USD @ BOC → CNY @ BCC | -0.4072% |
| RUB→CNY @ BCC → RUB @ BOC | -2.0825% |
| RUB→CNY @ BOC → RUB @ BCC | -4.4910% |
| JPY→USD @ SMBC → JPY @ BCC | -0.1376% |
| JPY→USD @ BCC → JPY @ SMBC | -0.4404% |
| KZT→CNY @ BCC → KZT @ BOC | -1.9774% |
| KZT→CNY @ BOC → KZT @ BCC | -3.0472% |
| KGS→USD @ MBANK → KGS @ Optima | -0.1143% |
| KGS→USD @ Optima → KGS @ MBANK | -0.3986% |
| KGS→RUB @ MBANK → KGS @ Optima | -4.3478% |
| KGS→KZT @ MBANK → KGS @ Optima | -6.0914% |
| TJS→EUR @ Amonat → TJS @ Eskhata | -0.4762% |

All omit interbank transfer costs, so actual bank-to-bank execution is worse unless another edge changes the route economics.

A third-party ForteBank discovery snapshot produced tiny apparent BCC→Forte differences around +0.0132% USD and +0.0909% EUR. They are deliberately not promoted: the Forte quote is third-party discovery and any real same-currency transfer has friction.

## Current Bybit Kazakhstan P2P correction

The earlier cross-time hypothesis of a very large KZT→USDT→KZT gain is not present in the fresher Bybit Kazakhstan surface.

Observed discovery values:

- buy USDT: 501.81 KZT;
- sell USDT: 480.00 KZT for 2m–4,999,999 KZT;
- 469.70 KZT for 100k–1,999,999 KZT;
- 466.80 KZT for 4,900–99,999 KZT.

Display-only round trips:

- 501.81→480.00: -4.3463%;
- 501.81→469.70: -6.3988%;
- 501.81→466.80: -6.9767%.

Therefore old/stale P2P pages cannot survive into a current execution graph.

## Long hybrid-chain sanity test

Research inputs:

- Binance BTC/USDT ask: 79,728.97;
- Bybit global BTC→RUB public P2P snapshot: 7,260,001.76 RUB/BTC;
- BCC CNY/RUB client-buy side: 12.8948 RUB/CNY;
- BCC USD/CNY client-buy side: 6.7153 CNY/USD;
- BCC USD→KZT client-sell side: 453.45 KZT/USD;
- Bybit Kazakhstan KZT→USDT: 501.81 KZT/USDT.

Route:

`USDT@Binance → BTC@Binance → RUB@BybitGlobalP2P → CNY@BCC → USD@BCC → KZT@BCC → USDT@BybitKZ`

Before explicit transfer costs and before the BTC spot fee:

`1 USDT → 0.9502341566 USDT`

Gross return:

**-4.9766%**.

With an illustrative 0.1% BTC spot fee:

**-5.0716%**.

This route is rejected before adding real transfer/settlement costs.

This is an important negative result: adding more hops does not create alpha; it merely expands the search space.

## Global graph algorithm

State identity is:

`asset @ venue / account / network / jurisdiction`

Examples:

- `USD@BCC:BUSINESS`
- `USD@DeutscheBank:CORPORATE`
- `CNY@VTB:BUSINESS`
- `CNY@BankOfChina:CORPORATE`
- `USDT@Binance:TREASURY/TRON`
- `USDT@Bybit:TREASURY/TRON`

Same asset on two venues requires an explicit transfer edge.

For a proportional edge:

`effective_rate = rate × (1 - fee)`

`weight = -ln(effective_rate)`

A proportional arbitrage candidate is a negative cycle.

The MetaPay implementation uses Bellman-Ford as the scalable `O(VE)` first-pass detector over the large graph. Recovered candidates are then repriced with exact amount-dependent rules:

- fixed fees;
- min/max limits;
- depth/slippage;
- inventory;
- freshness;
- settlement delay;
- account eligibility.

Exact simple-cycle enumeration remains available on a reduced candidate subgraph.

## Current conclusion

The research expanded MetaPay from a short crypto/P2P graph into a bank/payment/CEX/DEX graph with:

- 50 bank nodes;
- BIS global FX Top-20;
- 10 regional strategic currencies;
- initial 8-asset crypto extension;
- SWIFT/CIPS/Alipay+/UnionPay rail semantics;
- public/authenticated/on-demand evidence classes;
- scalable negative-cycle screening.

**No fully closed positive long cycle has yet been proven with every edge simultaneously fresh, account-eligible and executable after all transfer costs.**

That negative conclusion is deliberate and must be preserved until authenticated provider/bank APIs turn candidate edges into `LIVE_EXECUTABLE` edges.
