# 🧭 SYNERGY — Атлас 91 репозитория

> **Каноническая карта федерации Shtenco/SYNERGY.**  
> Архитектурный корень: [`Shtenco/synergy_system`](https://github.com/Shtenco/synergy_system)  
> Экономический master dossier: [`Shtenco/synergy_project`](https://github.com/Shtenco/synergy_project)  
> Цивилизационный граф: [`Shtenco/synergy_megaproject`](https://github.com/Shtenco/synergy_megaproject)  
> Runtime-оркестратор узла: [`Shtenco/synergy_meta_os`](https://github.com/Shtenco/synergy_meta_os)  
> **Срез live-реестра: 20 ноября 2026 · 91 репозиторий.**  
> Базовый глубокий паспорт: 75 репозиториев (28 сентября); 3 переименованных записи и 16 новых записей ожидают повторной глубокой проверки.

---

## Inventory refresh — 20 November 2026

The live GitHub inventory and `registry/SYNERGY_REPOSITORIES.json` now contain **91 repositories**. This refresh does not claim that all 91 have completed the original deep documentation pass.

- 72 entries retain a completed deep pass from the 75-repository September baseline.
- 3 renamed repositories require lineage and README revalidation.
- 16 newly inventoried repositories are classified provisionally and require the full README passport/deep pass.
- `synergy_project` remains the economic master dossier, not a child technology asset.
- `synergy_maps` is registered as a placeholder until an implementation appears.

### Newly inventoried repositories

| Repository | Provisional domain | Current role / evidence status |
|---|---|---|
| `synergy_complex_matrix_multiplication` | SCIENCE_RESEARCH | Structured complex-operator and matrix-free compute experiments |
| `synergy_computing_topology` | INFRA_NETWORK_SECURITY | Compact descriptor/index computing experiments |
| `synergy_search_engline` | INTELLIGENCE_AGENTS | Search/retrieval research shell |
| `synergy_lead_search_engline` | APPS_INTERFACES | Offline lead discovery and approval-gated CRM workflow |
| `synergy_triangle_money_system` | BLOCKCHAIN_MONETARY | Recursive collateral/liquidity simulation |
| `synergy` | MASTER_GOVERNANCE | Umbrella navigation and governance |
| `synergy_ai_llm_rwkv` | INTELLIGENCE_AGENTS | RWKV workflow and quantization research |
| `synergy_ai_economic` | FINANCE_REAL_ECONOMY | Economic digital-twin simulations |
| `synergy.github.io` | APPS_INTERFACES | Public presentation surface |
| `synergy_meta_api` | INFRA_NETWORK_SECURITY | API/MCP gateway prototype |
| `synergy_ai_workspace` | APPS_INTERFACES | Local AI workspace/desktop development |
| `synergistic_economics` | FINANCE_REAL_ECONOMY | Economic OS and endogenous-economy research |
| `synergy_metaverse` | APPS_INTERFACES | Spatial workspace projection/application |
| `synergy_maps` | APPS_INTERFACES | README-only placeholder |
| `shtenco_micro_ai` | INTELLIGENCE_AGENTS | MNN-Pocket-0.3B INT4 local inference tooling; external weights and device qualification pending |
| `synergy_long_term_harness` | INTELLIGENCE_AGENTS | README-only main; implementation currently on non-main branches |

### Repository rename reconciliation

- `binary_quantum_theory` → `synergy_binary_quantum_theory`
- `epstein_network` → `synergy_epstein_network`
- `multi_threaded_trading_robot_with_machine_learning_python` → `shtenco_multi_threaded_trading_robot_with_machine_learning_python`

These are identity/lineage updates, not additional assets. The registry keeps their deep-pass status pending until the renamed repository is revalidated.

**Important:** `federation_parent` is an architectural navigation hint only. It does not prove a runtime dependency, ownership transfer, or shared executable service. The live registry is the population source; this atlas's historical sections remain the September baseline until each pending entry receives its own deep pass.

---

## 🎯 Зачем нужен этот документ

SYNERGY больше нельзя корректно описывать как один репозиторий или один продукт. Это **федерация специализированных систем**, где разные репозитории отвечают за разные типы истины и не должны незаметно подменять друг друга.

Этот атлас решает четыре задачи:

1. показывает место каждого репозитория в общей системе;
2. отделяет архитектурную связь от доказанной runtime/code dependency;
3. задаёт единый стандарт README, аналогичный по глубине `dlp_solver`;
4. даёт человеку и AI-агенту единую точку входа в 91-репозиторную систему; статус паспортизации каждого узла отражён в машиночитаемом registry.

---

# 🧠 Система в одной схеме

```mermaid
flowchart TB
    HUMAN[👤 Человек / бизнес / исследователь]

    APPS[📱 Apps & Interfaces]
    GOV[🧭 SYNERGY SYSTEM\nArchitecture & Governance]
    META[⚙️ SYNERGY META-OS\nRuntime Orchestration]

    AI[🧠 NEXUS / AGI / Agents]
    TRADE[📈 MIDAS / Trading / Market Intelligence]
    FIN[💰 Financial OS / Pay / Real Economy]
    CHAIN[⛓️ Blockchain / Monetary / Trust]
    NET[🌐 Network / Security / Compression]
    SCI[🔬 Science / Megaproject]
    HOST[🐧 TURBO Linux / XPU Host]

    HUMAN --> APPS
    APPS --> GOV
    GOV --> META

    META --> AI
    META --> TRADE
    META --> FIN
    META --> CHAIN
    META --> NET
    META --> SCI
    META --> HOST

    AI --> TRADE
    AI --> SCI
    TRADE --> FIN
    FIN --> CHAIN
    CHAIN --> NET
    NET --> HOST
    SCI --> AI
    FIN --> SCI
```

## Ключевой принцип

```text
AI proposes            != monetary authority
payment evidence       != revenue
revenue                != profit
mint                    != external wealth
blockchain commitment  != economic truth by itself
UI state               != ledger state
service running        != service authorized
research hypothesis    != proven technology
```

---

# 🏛️ Иерархия мастер-репозиториев

```mermaid
flowchart TD
    SYS[🧭 synergy_system\nархитектура + governance + federation]
    PROJ[📘 synergy_project\nэкономический master dossier]
    MEGA[🌍 synergy_megaproject\nцивилизационный / научный граф]
    META[⚙️ synergy_meta_os\nruntime узла]
    APPS[📱 synergy_apps\nреестр приложений]

    NEXUS[🧠 synergy_agi_nexus]
    MIDAS[📈 synergy_midas_ai]
    FOS[💰 synergy_financial_os]
    BC[⛓️ synergy_ai_blockchain]

    SYS --> PROJ
    SYS --> MEGA
    SYS --> META
    SYS --> APPS
    SYS --> NEXUS
    SYS --> MIDAS
    SYS --> FOS
    SYS --> BC
```

### Семантика связей

| Тип | Смысл |
|---|---|
| **AUTHORITY** | Репозиторий является источником истины для своей области. |
| **ORCHESTRATES** | Запускает/координирует другие сервисы, но не присваивает их полномочия. |
| **CONSUMES** | Потребляет данные/артефакты другого слоя. |
| **PROVIDES** | Предоставляет данные/сервис/артефакт другому слою. |
| **R&D LINEAGE** | Исследовательская предыстория или экспериментальная ветка. |
| **PRESENTATION** | UI/сайт/витрина; не источник финансовой или научной истины. |
| **ARCHITECTURAL RELATION** | Связь в федерации документации; сама по себе не доказывает runtime dependency. |

---

# 📚 Единый стандарт README

Каждый репозиторий федерации должен иметь README с теми же дисциплинами, которые хорошо видны в `dlp_solver`:

```mermaid
flowchart LR
    A[🎯 Задача] --> B[🧠 Теория / идея]
    B --> C[🏗️ Архитектура]
    C --> D[🧪 Эксперименты / доказательства]
    D --> E[📊 Статус]
    E --> F[🗺️ Карта репозитория]
    F --> G[🔗 Место в SYNERGY]
    G --> H[🚀 Roadmap]
    H --> I[🛡️ Границы утверждений]
```

Минимально обязательны:

- понятная цель и роль;
- Mermaid/иконографика;
- архитектура;
- входы/выходы и authority boundaries;
- статус доказанности;
- воспроизводимость;
- карта файлов;
- связи с соседними репозиториями;
- roadmap;
- раздел «что проект НЕ утверждает»;
- ссылка на этот канонический атлас.

---

# 🧭 Полный реестр

> Полный owner inventory содержит 91 текущий репозиторий. 75 интерфейсных записей — отдельный contract/interface scope; 3 legacy interface names остаются unverified rename candidates. `federation_parent` — архитектурная навигация, не доказательство runtime dependency.

## 📱 Apps / interfaces

| Репозиторий | Роль в системе | Архитектурный родитель |
|---|---|---|
| [`shtenco.github.io`](https://github.com/Shtenco/shtenco.github.io) | Публичная web-витрина и навигационный интерфейс к проектам Shtenco. | [`synergy_apps`](https://github.com/Shtenco/synergy_apps) |
| [`shtencoauantai.github.io`](https://github.com/Shtenco/shtencoauantai.github.io) | Публичный web-интерфейс/сайт для представления отдельных направлений экосистемы. | [`synergy_apps`](https://github.com/Shtenco/synergy_apps) |
| [`sinergy_app`](https://github.com/Shtenco/sinergy_app) | Приложенческий shell/концепт SINERGY. | [`synergy_apps`](https://github.com/Shtenco/synergy_apps) |
| [`sinergy_super_app`](https://github.com/Shtenco/sinergy_super_app) | Концептуальная/продуктовая оболочка super-app для пользовательских сервисов SINERGY. | [`synergy_apps`](https://github.com/Shtenco/synergy_apps) |
| [`synergy_ai_workspace`](https://github.com/Shtenco/synergy_ai_workspace) | Local AI workspace and desktop application development; release/integration work remains branch-scoped. | [`synergy_apps`](https://github.com/Shtenco/synergy_apps) |
| [`synergy_app`](https://github.com/Shtenco/synergy_app) | Пользовательский финансовый интерфейс/приложение SINERGY. | [`synergy_apps`](https://github.com/Shtenco/synergy_apps) |
| [`synergy_app_family`](https://github.com/Shtenco/synergy_app_family) | Концептуальный семейный продуктовый слой/семейство приложений. | [`synergy_apps`](https://github.com/Shtenco/synergy_apps) |
| [`synergy_lead_search_engline`](https://github.com/Shtenco/synergy_lead_search_engline) | Offline lead-discovery workflow with FTS5, evidence review and approval-gated CRM hand-off. | [`synergy_apps`](https://github.com/Shtenco/synergy_apps) |
| [`synergy_maps`](https://github.com/Shtenco/synergy_maps) | Reserved geospatial/maps placeholder; no implementation present in the main branch at inventory refresh. | [`synergy_metaverse`](https://github.com/Shtenco/synergy_metaverse) |
| [`synergy_messenger`](https://github.com/Shtenco/synergy_messenger) | Мессенджер/коммуникационный слой SYNERGY и пользовательская клиентская оболочка. | [`synergy_apps`](https://github.com/Shtenco/synergy_apps) |
| [`synergy_metaverse`](https://github.com/Shtenco/synergy_metaverse) | Spatial/metaverse application and economic workspace projection layer. | [`synergy_system`](https://github.com/Shtenco/synergy_system) |
| [`synergy.github.io`](https://github.com/Shtenco/synergy.github.io) | Public Synergy web portal and presentation surface; not an economic authority. | [`synergy_apps`](https://github.com/Shtenco/synergy_apps) |
| [`synergychain.github.io`](https://github.com/Shtenco/synergychain.github.io) | Публичная web-витрина SINERGYCHAIN. | [`synergy_apps`](https://github.com/Shtenco/synergy_apps) |

## ⛓️ Blockchain / monetary systems

| Репозиторий | Роль в системе | Архитектурный родитель |
|---|---|---|
| [`print_money_synergychain`](https://github.com/Shtenco/print_money_synergychain) | R&D по программируемой эмиссии, ликвидности, mint/burn и внешне обеспеченному экономическому эффекту. | [`synergy_ai_blockchain`](https://github.com/Shtenco/synergy_ai_blockchain) |
| [`synergy_2chain_qe`](https://github.com/Shtenco/synergy_2chain_qe) | Двухцепочечный QE/арбитражный R&D и модели ликвидности на fork/DeFi окружениях. | [`synergy_ai_blockchain`](https://github.com/Shtenco/synergy_ai_blockchain) |
| [`synergy_ai_blockchain`](https://github.com/Shtenco/synergy_ai_blockchain) | Блокчейн/доверительный слой SYNERGY, включая PQ/EVM и привязку проверяемых состояний. | [`synergy_ai_blockchain`](https://github.com/Shtenco/synergy_ai_blockchain) |
| [`synergy_blochain_budget`](https://github.com/Shtenco/synergy_blochain_budget) | Блокчейн-трассируемость бюджетов/потоков и provenance финансовых операций. | [`synergy_ai_blockchain`](https://github.com/Shtenco/synergy_ai_blockchain) |
| [`synergy_chain`](https://github.com/Shtenco/synergy_chain) | Экспериментальная блокчейн- и token/economic-ветка SINERGYCHAIN. | [`synergy_ai_blockchain`](https://github.com/Shtenco/synergy_ai_blockchain) |
| [`synergy_chain_print_money`](https://github.com/Shtenco/synergy_chain_print_money) | Концептуальный узел интеграции chain-механики и monetary/emission R&D. | [`synergy_ai_blockchain`](https://github.com/Shtenco/synergy_ai_blockchain) |
| [`synergy_graph_print_money`](https://github.com/Shtenco/synergy_graph_print_money) | Графовый Economic OS / денежная топология и исследование внешне-обеспеченных контуров эмиссии. | [`synergy_ai_blockchain`](https://github.com/Shtenco/synergy_ai_blockchain) |
| [`synergy_metachain`](https://github.com/Shtenco/synergy_metachain) | Cross-chain/bridge архитектура и правила уникального lock/burn → mint/claim соответствия. | [`synergy_ai_blockchain`](https://github.com/Shtenco/synergy_ai_blockchain) |
| [`synergy_qe`](https://github.com/Shtenco/synergy_qe) | Концептуальный узел QE Engine; текущий main содержит только минимальный README. | [`synergy_ai_blockchain`](https://github.com/Shtenco/synergy_ai_blockchain) |
| [`synergy_triangle_money_system`](https://github.com/Shtenco/synergy_triangle_money_system) | Experimental recursive collateral, liquidity and triangular money-system simulation. | [`synergy_financial_os`](https://github.com/Shtenco/synergy_financial_os) |
| [`synergy_usds`](https://github.com/Shtenco/synergy_usds) | Экспериментальная денежная/стейблкоин-модель USDS и Base-fork экономика. | [`synergy_ai_blockchain`](https://github.com/Shtenco/synergy_ai_blockchain) |

## 💰 Finance / real economy

| Репозиторий | Роль в системе | Архитектурный родитель |
|---|---|---|
| [`synergistic_economics`](https://github.com/Shtenco/synergistic_economics) | Economic OS research core for accounting, settlement-adjacent mechanisms and endogenous economy simulation. | [`synergy_financial_os`](https://github.com/Shtenco/synergy_financial_os) |
| [`synergy_ai_economic`](https://github.com/Shtenco/synergy_ai_economic) | Economic digital-twin simulation and institutional regime experiments. | [`synergistic_economics`](https://github.com/Shtenco/synergistic_economics) |
| [`synergy_ai_financial_system`](https://github.com/Shtenco/synergy_ai_financial_system) | R&D по AI-управлению финансовыми моделями, капиталом и экономическими контурами. | [`synergy_financial_os`](https://github.com/Shtenco/synergy_financial_os) |
| [`synergy_cashero`](https://github.com/Shtenco/synergy_cashero) | Финансово-экономическая R&D-ветка, связанная с денежными потоками и платёжными сценариями. | [`synergy_financial_os`](https://github.com/Shtenco/synergy_financial_os) |
| [`synergy_eurasian`](https://github.com/Shtenco/synergy_eurasian) | Контур реальной экономики/индустрии и долгосрочной экономической архитектуры EURASIAN. | [`synergy_financial_os`](https://github.com/Shtenco/synergy_financial_os) |
| [`synergy_financial_os`](https://github.com/Shtenco/synergy_financial_os) | Канонический финансовый слой: учёт, NAV, обязательства, ликвидность, риск и экономическая истинность. | [`synergy_financial_os`](https://github.com/Shtenco/synergy_financial_os) |
| [`synergy_matrix_sota`](https://github.com/Shtenco/synergy_matrix_sota) | Владелец части debt/credit lifecycle механизмов и матричной оценки зрелости/архитектуры. | [`synergy_financial_os`](https://github.com/Shtenco/synergy_financial_os) |
| [`synergy_pay_system`](https://github.com/Shtenco/synergy_pay_system) | Платёжные маршруты, котировки, settlement/reconciliation и MetaPay-подобные контуры. | [`synergy_financial_os`](https://github.com/Shtenco/synergy_financial_os) |

## 🛡️ Infrastructure / network / security / compression

| Репозиторий | Роль в системе | Архитектурный родитель |
|---|---|---|
| [`dlp_solver`](https://github.com/Shtenco/dlp_solver) | Reverse-EXP / anti-exponential cryptographic research lab с эпистемической дисциплиной и воспроизводимыми экспериментами. | [`synergy_meta_os`](https://github.com/Shtenco/synergy_meta_os) |
| [`synegy_ai_compress`](https://github.com/Shtenco/synegy_ai_compress) | R&D по компрессии AI-данных/моделей и архивному субстрату. | [`synergy_meta_os`](https://github.com/Shtenco/synergy_meta_os) |
| [`synergy_computing_topology`](https://github.com/Shtenco/synergy_computing_topology) | Compact descriptor/index computing topology and repeated-query optimization experiments. | [`synergy_meta_os`](https://github.com/Shtenco/synergy_meta_os) |
| [`synergy_gguf_compress`](https://github.com/Shtenco/synergy_gguf_compress) | Лаборатория компрессии GGUF/LLM-моделей; на текущем main README остаётся минимальным, поэтому зрелость не предполагается. | [`synergy_meta_os`](https://github.com/Shtenco/synergy_meta_os) |
| [`synergy_meta_api`](https://github.com/Shtenco/synergy_meta_api) | Local API/MCP gateway prototype with read-only integration boundaries. | [`synergy_meta_os`](https://github.com/Shtenco/synergy_meta_os) |
| [`synergy_motherboard_xpu_xml`](https://github.com/Shtenco/synergy_motherboard_xpu_xml) | Экспериментальный аппаратно-описательный слой XPU/EML и конфигурация вычислительной платформы. | [`synergy_meta_os`](https://github.com/Shtenco/synergy_meta_os) |
| [`synergy_net`](https://github.com/Shtenco/synergy_net) | P2P/mesh/data-plane сеть и транспорт между узлами SYNERGY. | [`synergy_meta_os`](https://github.com/Shtenco/synergy_meta_os) |
| [`synergy_post_quantum_radio`](https://github.com/Shtenco/synergy_post_quantum_radio) | Концептуальный узел post-quantum radio/physical transport; текущий main пока не доказывает готовую реализацию. | [`synergy_meta_os`](https://github.com/Shtenco/synergy_meta_os) |
| [`synergy_qr_compress`](https://github.com/Shtenco/synergy_qr_compress) | Temporal dictionary / QR-compression R&D и повторное использование общей структуры данных. | [`synergy_meta_os`](https://github.com/Shtenco/synergy_meta_os) |
| [`synergy_shhts`](https://github.com/Shtenco/synergy_shhts) | Экспериментальный security/transport placeholder; назначение должно подтверждаться будущими артефактами, а не названием. | [`synergy_meta_os`](https://github.com/Shtenco/synergy_meta_os) |
| [`synergy_shttps`](https://github.com/Shtenco/synergy_shttps) | Экспериментальный secure-transport/HTTPS-like placeholder; реализация пока не должна считаться доказанной по одному названию. | [`synergy_meta_os`](https://github.com/Shtenco/synergy_meta_os) |
| [`synergy_turbo_linux`](https://github.com/Shtenco/synergy_turbo_linux) | Хостовый/OS-слой SYNERGY: системная изоляция, сервисы, устройство узла и экспериментальный runtime. | [`synergy_meta_os`](https://github.com/Shtenco/synergy_meta_os) |

## 🧠 Intelligence / agents

| Репозиторий | Роль в системе | Архитектурный родитель |
|---|---|---|
| [`shtenco_micro_ai`](https://github.com/Shtenco/shtenco_micro_ai) | Локальный inference runtime для MNN-Pocket-0.3B INT4; веса загружаются отдельно, а benchmark и качество должны быть подтверждены на целевом устройстве. | — |
| [`synergy_agentic_ai_economy`](https://github.com/Shtenco/synergy_agentic_ai_economy) | Экономика AI-агентов: задания, контракты, рынки, заработок и agent-to-agent workflows. | [`synergy_agi_nexus`](https://github.com/Shtenco/synergy_agi_nexus) |
| [`synergy_agi_autopilot`](https://github.com/Shtenco/synergy_agi_autopilot) | Агентный автопилот: планирование задач, DAG/оркестрация и ограниченное автономное исполнение. | [`synergy_agi_nexus`](https://github.com/Shtenco/synergy_agi_nexus) |
| [`synergy_agi_nexus`](https://github.com/Shtenco/synergy_agi_nexus) | Каноническая архитектура AGI NEXUS и поколений reasoning/world-model исследований. | [`synergy_agi_nexus`](https://github.com/Shtenco/synergy_agi_nexus) |
| [`synergy_agi_olga`](https://github.com/Shtenco/synergy_agi_olga) | Историческая линия OLGA/AGI и источник части поколений NEXUS. | [`synergy_agi_nexus`](https://github.com/Shtenco/synergy_agi_nexus) |
| [`synergy_ai_coder`](https://github.com/Shtenco/synergy_ai_coder) | Подсистема AI Coder и воспроизводимый compiler/build-tooling контур. | [`synergy_agi_nexus`](https://github.com/Shtenco/synergy_agi_nexus) |
| [`synergy_ai_company`](https://github.com/Shtenco/synergy_ai_company) | Концепт AI-native компании: агенты, процессы, контракты и автоматизация организации. | [`synergy_agi_nexus`](https://github.com/Shtenco/synergy_agi_nexus) |
| [`synergy_ai_language`](https://github.com/Shtenco/synergy_ai_language) | Семантический и языковой слой: формализация, язык взаимодействия и AI language tooling. | [`synergy_agi_nexus`](https://github.com/Shtenco/synergy_agi_nexus) |
| [`synergy_ai_llm_rwkv`](https://github.com/Shtenco/synergy_ai_llm_rwkv) | RWKV model workflow and experimental quantization/serving research. | [`synergy_agi_olga`](https://github.com/Shtenco/synergy_agi_olga) |
| [`synergy_gllm_nexus`](https://github.com/Shtenco/synergy_gllm_nexus) | Активный research runtime NEXUS/GLLM, бенчмарки, замороженные OOS-протоколы и генерации. | [`synergy_agi_nexus`](https://github.com/Shtenco/synergy_agi_nexus) |
| [`synergy_long_term_harness`](https://github.com/Shtenco/synergy_long_term_harness) | Исследовательский harness долгосрочной памяти и маршрутизации агентов; текущий main содержит README-only, реализация присутствует только в неосновных ветках. | — |
| [`synergy_nexus_science_agent`](https://github.com/Shtenco/synergy_nexus_science_agent) | Научный агент NEXUS: поиск, гипотезы, доказательства и исследовательская оркестрация. | [`synergy_agi_nexus`](https://github.com/Shtenco/synergy_agi_nexus) |
| [`synergy_search_engline`](https://github.com/Shtenco/synergy_search_engline) | Search engine research shell and retrieval experiments; main-branch implementation remains limited. | [`synergy_ai_language`](https://github.com/Shtenco/synergy_ai_language) |

## 🧭 Master / governance

| Репозиторий | Роль в системе | Архитектурный родитель |
|---|---|---|
| [`synergy`](https://github.com/Shtenco/synergy) | Umbrella governance and portfolio navigation repository; not an authority over child-domain ledgers. | [`synergy_system`](https://github.com/Shtenco/synergy_system) |
| [`synergy_apps`](https://github.com/Shtenco/synergy_apps) | Реестр и master-слой пользовательских приложений SYNERGY. | [`synergy_system`](https://github.com/Shtenco/synergy_system) |
| [`synergy_megaproject`](https://github.com/Shtenco/synergy_megaproject) | Цивилизационный master-graph: мегапроекты, фронтирные технологии, научные идеи и их доказательные связи. | [`synergy_system`](https://github.com/Shtenco/synergy_system) |
| [`synergy_meta_os`](https://github.com/Shtenco/synergy_meta_os) | Runtime-оркестратор полного узла SYNERGY поверх host OS и сетевых/AI/финансовых сервисов. | [`synergy_system`](https://github.com/Shtenco/synergy_system) |
| [`synergy_project`](https://github.com/Shtenco/synergy_project) | Master dossier: экономическая и продуктовая картина SYNERGY поверх архитектурного корня. | [`synergy_system`](https://github.com/Shtenco/synergy_system) |
| [`synergy_system`](https://github.com/Shtenco/synergy_system) | Главный архитектурный и governance-корень всей федерации SYNERGY. | — |

## 🔬 Science / research

| Репозиторий | Роль в системе | Архитектурный родитель |
|---|---|---|
| [`synergy_binary_quantum_theory`](https://github.com/Shtenco/synergy_binary_quantum_theory) | Теоретико-физическая исследовательская ветка Binary Quantum Gravity. | [`synergy_megaproject`](https://github.com/Shtenco/synergy_megaproject) |
| [`synergy_cold_nuclear`](https://github.com/Shtenco/synergy_cold_nuclear) | Воспроизводимый вычислительный R&D-контур для исследований низкоэнергетических/«cold nuclear» гипотез. | [`synergy_megaproject`](https://github.com/Shtenco/synergy_megaproject) |
| [`synergy_complex_matrix_multiplication`](https://github.com/Shtenco/synergy_complex_matrix_multiplication) | Structured complex-operator and matrix-free computation research; reported gains are scoped to measured kernels. | [`synergy_nexus_science_agent`](https://github.com/Shtenco/synergy_nexus_science_agent) |
| [`synergy_epstein_network`](https://github.com/Shtenco/synergy_epstein_network) | Отдельный исследовательский knowledge-graph/дистиллированный граф источников; не runtime-компонент финансовой системы. | [`synergy_megaproject`](https://github.com/Shtenco/synergy_megaproject) |

## 📈 Trading / market intelligence

| Репозиторий | Роль в системе | Архитектурный родитель |
|---|---|---|
| [`3D_bars_market_structure`](https://github.com/Shtenco/3D_bars_market_structure) | Эксперименты с трёхмерным представлением цена-время-объём и рыночной структурой. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`computer_vision_trading_metatrader_5`](https://github.com/Shtenco/computer_vision_trading_metatrader_5) | Исследования компьютерного зрения для распознавания рыночных структур и торговых сигналов. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`cross_forex_arbitrage_trading_metatrader_5`](https://github.com/Shtenco/cross_forex_arbitrage_trading_metatrader_5) | Исследовательский движок cross-FX и синтетического валютного арбитража. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`global_liquidity_dataminer`](https://github.com/Shtenco/global_liquidity_dataminer) | Сбор и подготовка глобальных макроликвидностных данных для рыночных моделей. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`midas_lite`](https://github.com/Shtenco/midas_lite) | Облегчённая исследовательская ветка MIDAS с торговыми прототипами и системами. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`quantum-trading_metatrader5`](https://github.com/Shtenco/quantum-trading_metatrader5) | Ранняя R&D-линия квантово-ассистированного трейдинга и интеграции с MetaTrader 5. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`shtenco_multi_threaded_trading_robot_with_machine_learning_python`](https://github.com/Shtenco/shtenco_multi_threaded_trading_robot_with_machine_learning_python) | Многопоточный ML-прототип торгового робота на Python. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`swap_arbitrage_metatrader_5`](https://github.com/Shtenco/swap_arbitrage_metatrader_5) | R&D по swap/carry-арбитражу и синтетическим портфелям в MetaTrader 5. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`synergy_adaptive_engine`](https://github.com/Shtenco/synergy_adaptive_engine) | Адаптивный движок параметров/режимов и переключения политик по состоянию рынка. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`synergy_agi_trader`](https://github.com/Shtenco/synergy_agi_trader) | AGI/AI трейдер: объединение reasoning и торговых контуров под риск-ограничениями. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`synergy_ai_investment_committee`](https://github.com/Shtenco/synergy_ai_investment_committee) | AI investment committee: агрегирование исследований и формирование ограниченных инвестиционных рекомендаций. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`synergy_ai_trade_terminal`](https://github.com/Shtenco/synergy_ai_trade_terminal) | Терминал и управляющий интерфейс для AI/algorithmic trading workloads. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`synergy_algotrading_graph_system`](https://github.com/Shtenco/synergy_algotrading_graph_system) | Графовая архитектура алгоритмического трейдинга, маршрутов и взаимосвязанных рыночных состояний. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`synergy_crypto_pump`](https://github.com/Shtenco/synergy_crypto_pump) | ML-исследования раннего обнаружения криптовалютных импульсов/pump-режимов. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`synergy_market_graph`](https://github.com/Shtenco/synergy_market_graph) | Граф рыночных сущностей, зависимостей и отношений для моделей/стратегий. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`synergy_market_maker`](https://github.com/Shtenco/synergy_market_maker) | Market-making R&D: котирование, inventory/risk и микроструктурные контуры. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`synergy_marketvision`](https://github.com/Shtenco/synergy_marketvision) | Рыночное восприятие/vision-layer для признаков, режимов и структур. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) | Интегрированный слой MIDAS AI: рыночный интеллект, модели и стратегия. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`synergy_midas_ai_trading_system`](https://github.com/Shtenco/synergy_midas_ai_trading_system) | Техническая и экспериментальная ветка MIDAS AI trading system. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`synergy_midas_institutional`](https://github.com/Shtenco/synergy_midas_institutional) | Институциональная архитектура MIDAS и интеграция data→model→portfolio→risk→execution. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`synergy_quantlab`](https://github.com/Shtenco/synergy_quantlab) | Quant R&D лаборатория для исследований стратегий, данных и статистических проверок. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`synergy_relative_value`](https://github.com/Shtenco/synergy_relative_value) | Relative-value/market-neutral исследования и сравнение относительных оценок. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`synergy_riskguard`](https://github.com/Shtenco/synergy_riskguard) | Независимый риск-контур, лимиты и veto-политики для торговых/финансовых систем. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |
| [`synergy_trademux`](https://github.com/Shtenco/synergy_trademux) | Маршрутизация и мультиплексирование торговых intents/стратегий к исполнимым каналам. | [`synergy_midas_ai`](https://github.com/Shtenco/synergy_midas_ai) |

**Branch inventory:** 1,292 refs across all 91 repositories; full names and HEAD SHAs are maintained in [JSON](https://github.com/Shtenco/synergy/blob/main/registry/BRANCH_INVENTORY_2026-11-20.json) and [CSV](https://github.com/Shtenco/synergy/blob/main/registry/BRANCH_INVENTORY_2026-11-20.csv).

# 🔄 Главные межсистемные контуры

## 1. Человек → приложение → runtime → authority

```mermaid
flowchart LR
    U[👤 Пользователь] --> APP[📱 app / messenger / web]
    APP --> META[⚙️ Meta-OS]
    META --> AUTH{Кто имеет authority?}
    AUTH --> AI[🧠 NEXUS]
    AUTH --> FIN[💰 Financial OS]
    AUTH --> PAY[💳 Pay System]
    AUTH --> CHAIN[⛓️ Blockchain]
    AUTH --> NET[🌐 SynergyNet]
```

UI не становится вторым ledger; Meta-OS не становится финансовым authority; AI не получает право перемещать деньги только потому, что умеет планировать.

## 2. Данные → интеллект → риск → исполнение

```mermaid
flowchart LR
    DATA[📡 Market / Macro / Alt Data] --> VISION[👁️ MarketVision / Graph / Features]
    VISION --> MIDAS[🧠 MIDAS AI]
    MIDAS --> IC[🏛️ AI Investment Committee]
    IC --> RISK[🛡️ RiskGuard]
    RISK --> MUX[🔀 TradeMux]
    MUX --> EXEC[⚡ Broker / Venue]
    EXEC --> SETTLE[✅ Settlement]
    SETTLE --> FOS[📚 Financial OS]
```

## 3. Экономика → внешняя стоимость → учёт

```mermaid
flowchart LR
    CAPITAL[💵 Capital] --> PROD[🏭 Productive / Market activity]
    PROD --> EXT[🌍 External cash flow]
    EXT --> PAY[💳 Settlement evidence]
    PAY --> FOS[📚 Double-entry / NAV]
    FOS --> ALLOC[♻️ Reinvestment / distribution]
```

## 4. Доверие и постквантовый транспорт

```mermaid
flowchart LR
    STATE[📦 Authoritative bytes] --> HASH[🔐 Hash / content address]
    HASH --> PQ[🛡️ PQ signatures / KEM research]
    PQ --> CHAIN[⛓️ Blockchain commitment]
    CHAIN --> NET[📡 Network / Radio]
    NET --> NODE[⚙️ SYNERGY node]
```

---

# 🧪 Эпистемическая дисциплина

Для всех 91 owner-inventory записей действует единая шкала:

| Метка | Значение |
|---|---|
| ✅ **GREEN** | Воспроизводимо подтверждено артефактами/тестами. |
| 🟡 **CANDIDATE** | Есть реализация/данные, но доказательство неполное. |
| 🔬 **R&D** | Исследовательская гипотеза или эксперимент. |
| 🧱 **STUB** | Архитектурный узел/README существует, полноценная реализация не доказана. |
| 🕰️ **LEGACY** | Историческая линия, сохраняемая ради provenance. |
| ❌ **RED** | Проверка провалена или тезис опровергнут. |

Ни название репозитория, ни диаграмма, ни наличие кода не переводят тезис автоматически в GREEN.

---

# 🗺️ Правило навигации

Каждый дочерний README должен содержать:

```text
SYNERGY SYSTEM
   ↓
domain master
   ↓
this repository
   ↓
related repositories
   ↓
inputs / outputs / evidence
```

И обратную ссылку:

- [SYNERGY SYSTEM](https://github.com/Shtenco/synergy_system)
- [Канонический атлас 91 репозитория](https://github.com/Shtenco/synergy_system/blob/main/docs/SYNERGY_REPOSITORY_ATLAS.md)
- [Машиночитаемый реестр](https://github.com/Shtenco/synergy_system/blob/main/registry/SYNERGY_REPOSITORIES.json)

---

# 🚀 Следующий уровень

После унификации README документация должна стать не только красивой, но и проверяемой машиной:

1. проверять, что все 91 README содержат системный паспорт;
2. проверять битые cross-repo links;
3. проверять authority conflicts;
4. строить Mermaid/Graphviz карту из JSON registry;
5. автоматически помечать STUB/LEGACY/R&D;
6. не позволять README утверждать GREEN без evidence artifact;
7. синхронизировать количество репозиториев и master links через CI.

---

## Коротко

```text
91 repositories
      ↓
one architecture root
      ↓
domain authorities
      ↓
explicit relations
      ↓
evidence-aware README
      ↓
one navigable SYNERGY system
```

**Цель документации — сделать федерацию понятной человеку и однозначной для AI-агентов, не подменяя красивой схемой реальные доказательства.**
