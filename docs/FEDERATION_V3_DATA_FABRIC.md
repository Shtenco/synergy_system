# SYNERGY Federation V3.1 — Data Fabric

**Status:** candidate architecture stacked on Federation V3 Contracts + Secure Event Fabric.  
**Scope:** archive, compression, content addressing, evidence preservation, offline payloads and persistent-state integration.  
**Technical federation:** 45 repositories.  
**Observed Shtenco repositories including the master dossier `synergy_project`: 46.**

## 1. Why this is a first-class federation layer

A full audit of current repository roots shows that archival/compression is not an isolated utility concern:

- `ai_compress` contains a family of lossless codecs, deduplication, random access and corpus benchmarks;
- `qr_compress` contains QTC1/QTC2 temporal dictionary compression and QF1 multi-frame offline transport;
- historical MIDAS defines a Unified Data Archive for raw data, features, signals, decisions, trades and latent states;
- Science Agent requires a content-addressed cache and reproducibility packages;
- Blockchain Budget requires a networked archive/data node for large official artifacts;
- SynergyNet already defines chunk→hash→dedup→compression→store-forward→reconstruct semantics;
- Meta-OS explicitly includes compression/content cache and storage lifecycle;
- XPU defines Persistent State as content-addressed programs, models, files and snapshots;
- Financial OS, MetaPay, blockchain and metachain all produce evidence objects that should be retained without giving the archive authority over their meaning.

Therefore Federation V3.1 introduces a cross-cutting **Data Fabric** rather than treating compression as a small helper.

## 2. Authority model

```text
Domain owner                    owns semantic truth
     │
     ├── canonical bytes
     │       ↓ SHA-256
     │  canonical_content_sha256
     │
     ▼
Data Fabric / ai_compress       owns codec/archive profiles, not domain truth
     │
     ├── encoded archive bytes
     │       ↓ SHA-256
     │  archive_sha256
     │
     ▼
SynergyNet                     transports opaque chunks/objects
     │
     ▼
Meta-OS                        places/caches/lifecycles services and artifacts
     │
     ├── Blockchain/MetaChain commit semantic/manifest digests
     └── XPU may later accelerate persistent-state storage/compute
```

### Non-negotiable rule

`archive authority != semantic authority`.

Examples:

- Financial OS owns an `ACCOUNTING_CLOSE`; `ai_compress` may encode it but cannot modify HardNAV.
- MetaPay owns settlement evidence; QR may carry a reference but cannot settle a payment.
- Science Agent owns a reproducibility package; compression does not turn a hypothesis into a scientific fact.
- Budget owns traceability semantics; the archive cannot manufacture a missing official source.

## 3. Dual-hash integrity model

Every lossless Data Fabric object binds at least two digests:

```text
canonical_content_sha256 = SHA256(canonical original bytes)
archive_sha256           = SHA256(exact encoded archive bytes)
```

This makes codec migration safe:

```text
canonical object
      ├── Gabriel Horn SGH1 archive
      ├── Zstd archive
      └── future codec archive

all share the same canonical_content_sha256
but have different archive_sha256 values.
```

A blockchain commitment that represents the semantic fact should bind the canonical content digest or a canonical manifest digest. It should not accidentally bind economic truth to one compression implementation.

## 4. Canonical archive source — `ai_compress`

Current technology families include:

- EGD-256;
- SABF-X;
- HACE-X;
- TSC-X;
- AMCE-100X;
- UMC-256 + MDL routing;
- Graph-AI Compression V5.2;
- GRAAL-IGC;
- Gabriel Horn Codec (`SGH1`): multiscale lifting, significance shells, deduplication, random access, surface-aware MDL;
- Arithmetic coding;
- rANS;
- Huffman;
- Graph Delta;
- Tier-1 engines and Matrix tooling.

No codec receives a universal-superiority claim. Promotion to a federation profile requires a named corpus, exact round-trip, archive size, encode/decode throughput, memory/RSS, random-access cost where relevant and a matched baseline.

## 5. Offline / temporal source — `qr_compress`

QTC1/QTC2 remains a distinct layer because its core property is **shared-model/temporal addressing + residual transport**, not simply general archive compression.

QTC2 profiles:

- `exact` — temporal address selects an exact shared-model entry;
- `patch` — temporal address selects a template and carries a residual;
- `standalone` — fallback for unrelated content.

Security/meaning boundary:

```text
timestamp address != infinite information
QR frame           != trust
signed QR ref      != payment authorization
model coverage     != compression ratio on arbitrary unseen data
```

QTC2 exact/patch objects must bind the shared model digest and temporal slot. Wrong-model or stale-model decode is a hard failure.

## 6. Storage tiers

| Tier | Purpose |
|---|---|
| `HOT_LOCAL` | active working state, low-latency domain data |
| `WARM_NODE_CACHE` | reusable local content/chunks |
| `DISTRIBUTED_SYNERGYNET` | replicated/distributed evidence objects |
| `COLD_IMMUTABLE_ARCHIVE` | long-lived audit/research/release artifacts |
| `AIR_GAPPED_QR_QTC` | compact offline transfer/reference path |
| `FUTURE_XPU_PERSISTENT_STATE` | future content-addressed XPU programs/models/files/snapshots |

Tier movement must preserve canonical digest and retention/access policy.

## 7. Domain integration map

### MIDAS

Archive:
- raw/normalized market data;
- features;
- graph snapshots;
- model checkpoints;
- signals and portfolio decisions;
- trade/execution evidence;
- validation/OOS reports;
- latent states where reproducibility requires them.

Historical `midas_ai_trading_system` Level 8 Unified Data Archive is migrated as a concept into this shared Data Fabric rather than reimplemented as a private archive silo.

### NEXUS / OLGA

Archive:
- frozen weights/checkpoints;
- architecture manifests;
- benchmark splits;
- inference traces;
- model digest/provenance;
- negative/failed benchmark evidence.

### Science Agent / scientific repos

Archive:
- retrieved source manifests;
- datasets;
- code/environment/seeds;
- computations;
- failed approaches;
- experiment/reproduction packages;
- citation-ready reports.

### Financial OS

Archive:
- ledger close packages;
- FinancialSnapshot / AccountingClose artifacts;
- Merkle roots/proofs;
- replay/restatement/reversal evidence;
- audit exports.

Financial OS remains semantic/accounting authority.

### MetaPay

Archive:
- PaymentIntent references where policy permits;
- execution receipts;
- settlement evidence;
- reconciliation packages;
- reversal evidence;
- provider-readiness evidence.

### Budget / GovTech

Archive:
- official raw artifacts;
- normalized public corpora;
- KBK registries and provenance;
- trace records;
- Merkle proof bundles;
- large backfill snapshots on archive/data nodes.

### Blockchain / MetaChain

Store/transport large proof bundles through Data Fabric; place compact cryptographic commitments on-chain. The chain does not become a bulk file store.

### Business OS / apps

- verified release/source bundles;
- encrypted user-controlled backup packages;
- offline receipt/evidence refs;
- optional compressed conversation/history packages subject to privacy/retention policy.

### XPU

Map Data Fabric content IDs/manifests to the future XPU `Persistent State` abstraction. Hardware acceleration is future R&D and must not be assumed available today.

## 8. SynergyNet codec policy

Best archive ratio is not necessarily best network profile. A transport selector should minimize an explicit operational cost:

```text
network_cost =
    bytes_on_wire
  + encode_cpu_cost
  + decode_cpu_cost
  + latency_penalty
  + memory_penalty
  + cache_amplification
```

Codec selection must be data-class and path aware. Small events may be sent raw; large repeated evidence can benefit from chunking/dedup; cold archives may optimize for ratio and random access rather than first-byte latency.

## 9. Security model

Required threat tests include:

- decompression bombs / extreme expansion ratio;
- malformed archive/parser fuzzing;
- third-party codec supply-chain risk;
- dictionary/shared-model poisoning;
- stale or wrong QTC model;
- dedup/cache-presence side channels;
- compression-oracle leakage around secret-dependent data;
- CPU/RAM/storage exhaustion;
- unauthorized retention of user/financial data;
- raw secret material inside archive packages;
- corrupted/reordered/missing QR frame sets;
- replay of expired offline payloads.

No archive manifest contains raw private keys, mnemonics or seed phrases. Encryption uses external key references; custody remains in the relevant KMS/HSM/user boundary.

## 10. Promotion gates

A Data Fabric codec/profile progresses through:

`R&D → CORPUS_VERIFIED → INTEGRATION_TESTED → FAILURE_TESTED → SANDBOX_PROFILE → PRODUCTION_ELIGIBLE`

Production eligibility requires:

1. exact round-trip corpus evidence;
2. parser/resource hardening;
3. deterministic manifest binding;
4. documented license/supply-chain status;
5. benchmark against established baselines;
6. privacy/security review;
7. rollback/codec migration procedure;
8. domain-specific retention/compliance approval.

## 11. First cross-domain E2E target

```text
Financial OS AccountingClose canonical bytes
        ↓ canonical_content_sha256
ai_compress selected lossless profile
        ↓ archive_sha256 + ArchiveManifest
SynergyNet durable object/chunk transport
        ↓
remote Data Fabric cache/archive node
        ↓ decode
verify canonical_content_sha256
        ↓
AI Blockchain commits canonical/manifest digest
        ↓
MetaChain verifies source commitment
```

A second target uses a QTC2/QF1 offline reference to the same archive object without granting any financial authority.

## 12. Repository-count distinction

Federation V3 contains 45 technical repositories. `Shtenco/synergy_project` was created later as the master grant/investor/regulatory dossier and is not a new runtime authority. The current account-level observation is therefore:

```text
technical federation repos = 45
master dossier repos        = 1
observed Shtenco repos      = 46
```

This distinction must be used in future README, audits and valuation documents.
