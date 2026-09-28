# ⚙️ SYNERGY EXECUTABLE TOPOLOGY V1

> Срез: 28 сентября 2026.
> Цель: показать не всю желаемую архитектуру, а **фактически материализованные typed boundaries** и оставшиеся разрывы.

## 1. Текущий системный срез

```text
Repositories                         75
Typed contract families             17
Runtime edges ADAPTER_IMPLEMENTED   10
Runtime edges E2E_TESTED             0
Runtime edges DEPLOYED               0

Repository interface states:
  ADAPTER_INTEGRATED                12
  PARTIAL_IMPLEMENTATION             1
  CONTRACT_DEFINED                   7
  ARCHITECTURAL_ONLY                55
```

Главное: SYNERGY уже перестала быть только документационной федерацией, но ещё не является полностью E2E-запущенной distributed OS.

---

# 2. Плоскости истины

```mermaid
flowchart TB
    I[🧠 INTELLIGENCE\nproposal / inference]
    V[🧪 VALIDATION\nprotocol result]
    R[🛡️ RISK\nallow / resize / veto]
    X[⚡ EXECUTION\nroute / fill]
    S[💳 SETTLEMENT\nexternal evidence / reconciliation]
    A[💰 ACCOUNTING\nclassification / ledger / NAV]
    T[⛓️ TRUST\ncommitment / finality]
    P[📱 PRESENTATION\nread-only view]

    I --> V --> R --> X --> S --> A --> T --> P
```

Ни одна стрелка не означает перенос authority. Каждый слой владеет только своим типом факта.

---

# 3. Вертикаль A — AI-assisted institutional trading

```mermaid
flowchart LR
    N[🧠 NEXUS] -->|ai.proposal/v1\nadvisory only| M[📈 MIDAS]
    M -->|portfolio-decision/v1| Q[🧪 QuantLab]
    Q -->|validation-decision/v1| R[🛡️ RiskGuard]
    R -->|risk-decision/v1| X[🔀 TradeMux]
    X -->|execution-result/v1| P[💳 Pay]
    P -->|settlement-evidence/v1| F[💰 Financial OS]
    F -->|accounting-recognition/v1| B[⛓️ AI Blockchain]
```

### Enforcement

```text
NEXUS proposal        != authorization
MIDAS proposal        != validation pass
validation pass       != risk permission
risk permission       != fill
fill                  != settlement
settlement            != revenue
accounting recognition!= blockchain-created truth
```

`NEXUS → MIDAS` специально реализован как `authorization=false` + `requires_domain_validation=true`.

---

# 4. Вертикаль B — Real Economy / capital deployment

```mermaid
flowchart LR
    E[🏭 Eurasian / EIIOM] -->|project-proposal/v1| G[🏛️ Capital Governance\nsynergy_project]
    G -->|funding-authorization/v1| P[💳 Pay]
    P -->|settlement-evidence/v1| F[💰 Financial OS]
    F --> B[⛓️ AI Blockchain]
```

### Исправленный causal invariant

Старый shortcut:

```text
optimizer/project proposal → Financial OS
```

запрещён.

Новый путь:

```text
project proposal
→ explicit underwriting/governance
→ bounded authorization
→ payment execution
→ external settlement/reconciliation
→ accounting recognition
```

`ProjectProposal` не может self-authorize. `AUTHORIZE` требует approver provenance, underwriting evidence, expiry, currency, payment rails и максимальную сумму.

---

# 5. Вертикаль C — Artifact / runtime integrity

```mermaid
flowchart LR
    C[🗜️ AI Compress] -->|archive.evidence/v1| M[⚙️ Meta-OS]
    M -->|node-manifest/v1| H[🐧 TURBO Linux target]
    C -. future .-> N[🌐 SynergyNet]
```

Материализовано:

- AI Compress создаёт evidence только при exact byte round-trip;
- archive SHA-256 и byte size входят в contract;
- Meta-OS сверяет evidence с реальным artifact file;
- Meta-OS уже умеет hash-check manifests, role/capability ceilings, attestation, resource limits и fail-closed dangerous capabilities.

`Meta-OS → TURBO Linux` пока только producer-implemented: TURBO consumer contract ещё не материализован.

---

# 6. Engineering lineage

```mermaid
flowchart LR
    L[🧬 AI Language] -->|requirement-trace/v1| C[👨‍💻 AI Coder]
    C -->|change-evidence/v1| M[⚙️ Meta-OS]
```

Текущее состояние:

- AI Language producer реально строится из `SemanticTrace`, `REQ-*`, mutation/validation events и coverage;
- AI Coder в текущем `main` пока не имеет executable consumer/runtime, поэтому edge остаётся `CONTRACT_DEFINED`;
- Meta-OS не принимает generated code как deployment permission.

---

# 7. Scientific lineage

```mermaid
flowchart LR
    N[🧠 NEXUS] --> SA[🔬 Science Agent]
    SA -->|science.evidence-package/v1| M[🌍 Megaproject]
```

Контракты определены, но Science Agent `main` пока архитектурный bootstrap. Поэтому runtime edges не создаются искусственно.

---

# 8. Trust / cross-chain / UI lineage

```mermaid
flowchart LR
    F[💰 Financial OS] --> B[⛓️ AI Blockchain]
    B -. trust.commitment/v1 .-> MC[🌉 MetaChain]
    B -. trust.commitment/v1 .-> A[📱 Apps]
```

Financial OS → Blockchain уже materialized через authority-preserving domain commitment.

MetaChain и Apps consumers пока не доказаны executable adapters, поэтому остаются contract-defined.

---

# 9. Machine-readable control plane

Канонические файлы:

```text
registry/SYNERGY_REPOSITORIES.json
registry/AUTHORITY_REGISTRY.json
registry/CONTRACT_REGISTRY.json
registry/DEPENDENCY_GRAPH.json
registry/REPOSITORY_INTERFACES.json
registry/INTEGRATION_GAPS.json
registry/INVARIANT_REGISTRY.json
```

Их назначение:

| Registry | Ответ на вопрос |
|---|---|
| Repository Registry | какие 75 репозиториев входят в систему? |
| Authority Registry | кто владеет каким типом истины? |
| Contract Registry | какие typed artifacts существуют? |
| Dependency Graph | какие связи архитектурные, contract или runtime? |
| Repository Interfaces | что каждый repo производит/потребляет? |
| Integration Gaps | какой endpoint отсутствует для следующего promotion? |
| Invariant Registry | какие shortcuts система обязана запрещать? |

---

# 10. Contract representations

Для V1 используются три representations:

```text
JSON Schema 2020-12  → canonical language-neutral validation
Pydantic V2          → Python reference implementation
Protobuf             → RPC / binary wire representation
```

Breaking semantic change требует нового major contract ID (`.../v2`).

---

# 11. Evidence and trace

Канонический Evidence ID:

```text
urn:synergy:evidence:<repo>:<kind>:sha256:<digest>
```

Один `trace_id` должен проходить через целый causal process. Evidence ID доказывает identity байтов/артефакта, но не автоматически истинность claim.

---

# 12. Что блокирует E2E_TESTED

Первый cross-repo harness уже существует:

```text
integration/trading_truth_path/
```

но promotion не выполнен, потому что GitHub Actions текущего private repo создаёт jobs, завершающиеся без выполненных steps; job logs недоступны. Поэтому CI намеренно не помечен GREEN.

Следующий promotion допускается только после фактического запуска pinned checkout набора и evidence bundle.

---

# 13. Следующие самые ценные endpoints

По `INTEGRATION_GAPS.json` приоритеты:

1. Science Agent producer/consumer runtime;
2. AI Coder consumer requirement-trace + producer change-evidence;
3. TURBO Linux consumer node-manifest;
4. SynergyNet consumer archive evidence + producer transport evidence;
5. MetaChain consumer trust commitment;
6. Apps read-only accounting/trust consumers;
7. полный cross-repo E2E harness торгового и real-economy paths.

---

# 14. Архитектурный критерий зрелости

SYNERGY становится операционной системой не тогда, когда все 75 repos имеют стрелки, а когда для каждой важной стрелки можно ответить:

```text
What contract_id?
What schema_version?
Who is producer?
Who is canonical authority?
Who is consumer?
What exact bytes were transferred?
What evidence_id proves the transition?
What trace_id connects it to reality?
What status is proven: DEFINED / ADAPTER / E2E / DEPLOYED?
```

Именно этот принцип теперь является основой дальнейшей интеграции федерации.
