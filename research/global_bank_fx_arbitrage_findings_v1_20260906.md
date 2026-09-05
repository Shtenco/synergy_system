# Global Bank FX × Payment Rails × MetaPay Arbitrage Research v1

Date: 2026-09-06  
Target price date: 2026-09-05, with latest previous business-day quote where the target date is not available.  
Status: research evidence, **not execution proof**.

## Scope

Engineering universe:

- 50 banks / institutional bank nodes;
- 20 fiat currencies: `USD EUR GBP CHF JPY CNY HKD SGD AED TRY RUB KZT UZS KGS TJS BYN GEL INR KRW THB`;
- regions: CIS/Central Asia/Georgia, Europe, Asia;
- rails: SWIFT, SEPA, CIPS/CNAPS, Alipay+, UnionPay, local transfers, authenticated bank APIs/traders;
- crypto bridge nodes remain handled by MetaPay/CEX/DEX graph separately.

This is not a formal ranking of banks by assets. Banks were selected for cross-border FX/payment relevance and public/API research utility.

## Research result: a 50×20 live public price matrix does not exist

Banks expose FX in materially different ways:

1. fresh public bid/ask table;
2. delayed/stale public table;
3. authenticated API;
4. authenticated app/dealer/trader;
5. on-demand relationship-manager/dealing quote;
6. capability/rail documentation only.

Therefore the project deliberately stores:

- a **50-bank capability/quote-mode registry**; and
- a separate **fresh quote snapshot** containing actual prices only when sourced.

A bank that supports CNY does not automatically create a priced CNY edge.

## Strong public/current bank quote nodes found

### Bank CenterCredit — Kazakhstan

Fresh 2026-09-05 public KZT and cross-rate table contains USD, EUR, RUB, GBP, CNY, AED, CHF, TRY, UZS, JPY and cross pairs including:

- USD/CNY 6.7021 / 6.7153;
- CNY/RUB 12.6838 / 12.8948;
- USD/JPY 156.055 / 156.459;
- USD/CHF 0.808 / 0.812;
- USD/AED 3.6674 / 3.6786;
- EUR/USD 1.16034 / 1.16168.

This is a valuable public graph hub, but public pricing is not account-eligibility proof.

### Optima Bank — Kyrgyzstan

2026-09-05 non-cash rates explicitly apply to legal entities/IP up to USD 10,000 equivalent:

- USD/KGS 87.40 / 87.80;
- EUR/KGS 101.20 / 102.20;
- KZT/KGS 0.185 / 0.200;
- RUB/KGS 0.990 / 1.040;
- CNY/KGS 12.25 / 13.75.

Above the threshold, negotiated Treasury pricing is required.

### Kapitalbank — Uzbekistan

2026-09-05 business/legal entity table:

- USD/UZS 11,759.62 / 11,830.39;
- EUR/UZS 13,562 / 13,835.71;
- RUB/UZS 129.01 / 137.43.

### Bank of China — China

2026-09-05 public BOC table creates a major CNY hub including USD/EUR/GBP/CHF/JPY/HKD/SGD/AED/THB/TRY/KRW plus directly RUB and KZT.

Examples, normalized from source scale of 100 foreign units:

- USD→CNY bank buy: 6.7013 CNY/USD;
- CNY→USD client cost: 6.7295 CNY/USD;
- RUB→CNY: 0.0753 CNY/RUB;
- CNY→RUB: 12.6262626 RUB/CNY from bank-sell RUB side;
- KZT→CNY: 0.0144 CNY/KZT;
- CNY→KZT: 66.6666667 KZT/CNY from bank-sell KZT side.

### SMBC — Japan

2026-09-05 public internet FX-deposit rates:

- USD/JPY TTB/TTS 155.77 / 156.27;
- EUR/JPY 180.76 / 181.46;
- GBP/JPY 209.21 / 211.21;
- CHF/JPY 192.46 / 192.91.

These are useful research prices but are not automatically corporate SWIFT prices.

### MUFG — Japan

Latest previous business day, 2026-09-04:

- USD/JPY 154.68 / 156.68 TTB/TTS;
- EUR/JPY 179.57 / 182.57;
- GBP/JPY 206.68 / 214.68;
- CHF/JPY 191.82 / 193.62.

### MBANK — Kyrgyzstan

2026-09-04 non-cash:

- USD/KGS 87.45 / 87.50;
- EUR/KGS 101.40 / 102.40;
- RUB/KGS 0.986 / 1.035;
- KZT/KGS 0.182 / 0.197.

Promotional SWIFT through 2026-09-30:

- USD 0.2%, min USD35, max USD300;
- CNY 0.2%, min CNY50, max CNY1000.

### Bank Eskhata — Tajikistan

2026-09-04 public conversion page includes USD/EUR/RUB and a broader block containing CNY/KZT/AED/TRY. Exact individual-vs-legal-entity subsection must be bound before production use.

## API / authenticated-price hubs

### TBC Bank — Georgia

Production API supports commercial buy/sell rates and cross conversion, requiring developer API credentials. This is one of the strongest future MetaPay bank adapters because the price can be machine-fetched rather than scraped.

### Bank of Georgia

Business API documentation includes commercial/cross rates and conversion-order creation. Human/account authorization remains required.

### Eurasian Bank — Kazakhstan

Smart Business advertises real-time market pricing, narrow spreads, multiple online currency pairs and zero separate conversion commission. Price is authenticated.

### Deutsche Bank FX4Cash

Links real-time FX conversion to payment execution across a broad global payment-currency set. Authenticated/pre-agreed pricing.

### Commerzbank FX Live Trader

Real-time corporate prices over 100+ FX pairs. Authenticated trader edge.

### DBS FX Online

Live transparent authenticated pricing for 40+ pairs; broader FX service supports 130+ currencies and TT supports 33 currencies.

### UOB Business

Telegraphic transfer supports multiple currencies and real-time FX locking through authenticated business channels.

## Payment rails are edges, not FX prices

### SWIFT

SWIFT transports/coordinates cross-border payments. It does not provide a universal executable FX rate. Every SWIFT edge needs:

- sender bank/account;
- receiver bank/account;
- currency;
- OUR/SHA/BEN fee semantics where applicable;
- correspondent/intermediary fees;
- cut-off;
- settlement time;
- bank FX quote if conversion happens.

### CIPS

CIPS is a major RMB settlement rail, not an FX-rate source. It is valuable because it can connect CNY accounts across regions without pretending the transport layer creates a price.

### Alipay+

Alipay+ is modeled as merchant payment/acquiring/settlement infrastructure, **not as a generic treasury CNY↔crypto converter**. Its Pay API can return `settlementAmount` and `settlementQuote` when transaction and settlement currencies differ. That API quote may become a real merchant-payment edge after authentication. Settlement reports are reconciliation evidence, not an FX quote.

### UnionPay

UnionPay's published exchange rate is a card-network reference; issuer fees are excluded and transaction/settlement date can matter. It is not a corporate SWIFT/dealing quote.

## Cross-bank sanity tests — before transfer costs

The first cross-bank public-price comparisons did **not** prove positive arbitrage.

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

These values omit interbank transfer costs. Real settlement costs can only worsen them unless another market edge changes the route.

A third-party ForteBank snapshot created extremely small apparent BCC→Forte gross differences:

- USD: about +0.0132%;
- EUR: about +0.0909%.

These are **not** promoted because:

- the Forte price is third-party discovery rather than authenticated business execution;
- same-currency transfer between the two bank states is not free;
- the apparent edge is smaller than realistic operational friction.

## Current P2P sanity correction

The earlier cross-snapshot hypothesis of a very large KZT→USDT→KZT P2P gain is not present in the fresher Bybit Kazakhstan surface.

Current public discovery values:

- buy USDT: 501.81 KZT;
- sell USDT: 480.00 KZT for the 2m–4,999,999 KZT band;
- 469.70 KZT for 100k–1,999,999 KZT;
- 466.80 KZT for 4,900–99,999 KZT.

Corresponding display-only round trips:

- 501.81→480.00: **-4.3463%**;
- 501.81→469.70: **-6.3988%**;
- 501.81→466.80: **-6.9767%**.

Therefore stale/cross-time P2P quotes must never survive into the live graph.

## Long hybrid chain sanity test

Using contemporaneous/recent research inputs:

- Binance BTC/USDT ask: 79,728.97;
- Bybit global BTC→RUB P2P snapshot: 7,260,001.76 RUB/BTC;
- BCC CNY/RUB client-buy side: 12.8948 RUB/CNY;
- BCC USD/CNY client-buy side: 6.7153 CNY/USD;
- BCC USD→KZT client-sell side: 453.45 KZT/USD;
- Bybit Kazakhstan KZT→USDT: 501.81 KZT/USDT.

Research route:

`USDT@Binance → BTC@Binance → RUB@BybitGlobalP2P → CNY@BCC → USD@BCC → KZT@BCC → USDT@BybitKZ`

Before explicit transfer costs and before the BTC spot trading fee:

`1 USDT → 0.9502341566 USDT`

Gross return:

**-4.9766%**.

With a 0.1% illustrative BTC spot fee:

**-5.0716%**.

This route is therefore rejected even before operational transfer/settlement costs.

This is an important negative result: the global graph destroys the earlier false impression that adding more hops automatically increases profit.

## Why long cycles still matter

Long-cycle search remains necessary because an edge that is uninteresting in isolation may be useful as an intermediate state. Candidate route shape:

`KZT@BankA → CNY@BankB → JPY@BankC → USD@BankD → USDC@CEX → BTC@CEX → RUB@P2P → KZT@BankE`

But every transition needs a real priced edge. Adding an unsupported reference conversion is forbidden.

## Graph construction rule

State identity is:

`asset @ venue/account/network/jurisdiction`

Examples:

- `USD@BCC:BUSINESS`
- `USD@DeutscheBank:CORPORATE`
- `CNY@VTB:BUSINESS`
- `CNY@BankOfChina:CORPORATE`
- `USDT@Binance:TREASURY/TRON`
- `USDT@Bybit:TREASURY/TRON`

Same asset on different venues requires a transfer edge.

## Current conclusion

The 50-bank/20-currency research materially increases the graph's connectivity, especially through:

- BCC multi-currency cross rates;
- BOC CNY hub;
- JPY hubs at SMBC/MUFG;
- Central Asian non-cash local-currency pairs;
- CIPS/CNAPS for RMB settlement;
- SWIFT/ISO 20022 for cross-border settlement;
- authenticated API/trader hubs such as TBC, Bank of Georgia, Deutsche Bank, Commerzbank and DBS;
- MetaPay CEX/P2P/DEX nodes.

However, **no fully closed positive long cycle has yet been proven with every edge simultaneously fresh, account-eligible and executable after all transfer costs**.

That is the correct research result at this stage.

The next proof step is to connect authenticated bank/provider APIs and let `GlobalRouteGraph.execution_cycles()` search only `LIVE_EXECUTABLE` edges.
