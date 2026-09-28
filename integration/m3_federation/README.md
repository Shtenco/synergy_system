# SYNERGY M3 Federation — Edge-Complete E2E Gate

Этот harness является promotion gate после M2 endpoint closure.

## Что изменилось в M3 V2

M3 больше не считается доказанным по набору разрозненных unit/contract tests.

Единый запуск должен доказать **все 22 cross-repository runtime edge**, которые в `registry/REPOSITORY_INTERFACES.json` имеют статус `ADAPTER_IMPLEMENTED`.

```text
20 pinned repositories
        ↓
6 executable verticals
        ↓
22 exact producer → consumer witnesses
        ↓
evidence bundle v2
        ↓
verify_evidence.py
        ↓
только после наблюдаемого PASS:
ADAPTER_IMPLEMENTED → E2E_TESTED
```

## Исполняемые вертикали

### Trading

```text
NEXUS
→ MIDAS
→ QuantLab
→ RiskGuard
→ TradeMux
→ Pay
→ Financial OS
→ AI Blockchain
```

Trading path передаёт runtime payloads через всю цепочку. Проверка `Financial OS → AI Blockchain` использует SHA-256 фактического accounting payload и динамический Rust consumer, а не фиксированный fixture hash.

### Science

```text
NEXUS → Science Agent → Megaproject
```

### Engineering

```text
AI Language → AI Coder → Meta-OS
```

### Real economy

```text
NEXUS → Eurasian → Capital Governance → Pay
```

### Runtime / network

```text
AI Compress → SynergyNet
AI Compress → Meta-OS
SynergyNet → Meta-OS
SynergyNet → AI Blockchain
Meta-OS → TURBO Linux
```

### Trust / UI

```text
Financial OS → Apps
AI Blockchain → MetaChain
AI Blockchain → Apps
```

## Evidence V2

Успешный запуск создаёт:

`integration/m3_federation/evidence/m3_federation_result.json`

Файл содержит SHA-256 federation lock, 20 pinned repository commits, результаты шести вертикалей, ровно 22 edge witnesses и сведения о runtime-платформе.

`verify_evidence.py` не доверяет только числу 22. Он заново читает `registry/REPOSITORY_INTERFACES.json` и требует точного совпадения множества witness edges с текущим registry.

## Запуск

```bash
export SYNERGY_REPOS_ROOT=/path/to/sibling/checkouts
export SYNERGY_VERIFY_LOCK=1
python synergy_system/integration/m3_federation/run.py
python synergy_system/integration/m3_federation/verify_evidence.py
```

## Promotion rule

Наличие harness, workflow или adapter-кода **не означает `E2E_TESTED`**.

Статус повышается только после фактического наблюдаемого успешного исполнения pinned checkout-набора и прохождения verifier:

```text
CONTRACT_DEFINED
→ PRODUCER_IMPLEMENTED
→ CONSUMER_IMPLEMENTED
→ ADAPTER_IMPLEMENTED
→ E2E_TESTED
→ DEPLOYED
```

До такого запуска registry обязан сохранять `E2E_TESTED = 0`.
