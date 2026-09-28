# SYNERGY M3 Federation Semantic E2E

Этот harness является следующим promotion gate после M2 endpoint closure.

Он проверяет реальные producer→consumer переходы между независимыми репозиториями:

- NEXUS → Science Agent → Megaproject;
- AI Language → AI Coder → Meta-OS;
- Eurasian → Capital Governance → Pay;
- AI Compress → SynergyNet → Meta-OS → TURBO;
- SynergyNet → Rust AI Blockchain transport consumer;
- Financial OS → Apps read-only accounting;
- AI Blockchain (Rust trust fixture producer) → MetaChain → Apps.

## Статус

Наличие harness **не означает E2E_TESTED**. Статус повышается только после фактического успешного исполнения pinned checkout-набора.

## Запуск

```bash
export SYNERGY_REPOS_ROOT=/path/to/sibling/checkouts
export SYNERGY_VERIFY_LOCK=1
python synergy_system/integration/m3_federation/run.py
```

`integration_lock_v1.json` фиксирует точные commit SHA для воспроизводимости.
