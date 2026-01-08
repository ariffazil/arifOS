# arifOS v46 8-Folder Orthogonal Architecture

**Visual Code Structure Map**

---

## 🏛️ High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          arifOS v46 CORE                                 │
│                    "DITEMPA BUKAN DIBERI"                                │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
            ┌───────▼───────┐ ┌────▼────┐ ┌────────▼────────┐
            │   AGI (Δ)     │ │ ASI (Ω) │ │   APEX (Ψ)     │
            │  Mind/Logic   │ │Heart/Care│ │  Soul/Judge    │
            └───────┬───────┘ └────┬────┘ └────────┬────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
            ┌───────▼───────┐ ┌────▼────┐ ┌────────▼────────┐
            │ ENFORCEMENT   │ │INTEGRATION│ │    SYSTEM      │
            │   (Police)    │ │(Interface)│ │  (Lifecycle)   │
            └───────┬───────┘ └────┬────┘ └────────┬────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                            ┌───────▼───────┐
                            │    MEMORY     │
                            │   (Storage)   │
                            └───────────────┘
```

---

## 📂 File System Structure (8 Canonical Zones)

```
arifos_core/
│
├── 🧠 agi/                         # AGI Kernel (Δ Delta - Mind)
│   ├── __init__.py                 # AGI floor checks export
│   ├── floor_checks.py             # F1 Truth, F2 ΔS checks
│   ├── atlas.py                    # ATLAS-333 lane classifier
│   └── clarity_scorer.py           # ΔS computation
│
├── ❤️  asi/                         # ASI Kernel (Ω Omega - Heart)
│   ├── __init__.py                 # ASI floor checks export
│   ├── floor_checks.py             # F3 Peace², F4 κᵣ, F5 Ω₀, F7 RASA
│   ├── eureka.py                   # EUREKA-777 paradox synthesis
│   └── cooling.py                  # SABAR protocol
│
├── 👁️  apex/                        # APEX Kernel (Ψ Psi - Soul)
│   ├── __init__.py                 # APEX floor checks export
│   ├── floor_checks.py             # F6 Amanah, F8 Tri-Witness, F9 Anti-Hantu
│   ├── contracts/                  # Constitutional contracts
│   │   └── apex_prime_output_v41.py
│   └── governance/                 # Governance modules
│       ├── fag.py                  # Full Autonomy Governance
│       ├── ledger.py               # Ledger management
│       ├── ledger_cryptography.py  # Crypto primitives
│       ├── merkle.py               # Merkle tree
│       ├── proof_of_governance.py  # PoG protocol
│       ├── session_physics.py      # Session physics
│       ├── sovereign_signature.py  # Signature verification
│       ├── vault_retrieval.py      # Vault access
│       └── zkpc_runtime.py         # Zero-knowledge proofs
│
├── 👮 enforcement/                  # Enforcement Zone (Police)
│   ├── metrics.py                  # Core floor check functions
│   ├── trinity_orchestrator.py     # Trinity AAA orchestrator
│   ├── wisdom_gated_release.py     # Budi graduated verdicts
│   ├── response_validator.py       # Response validation
│   ├── genius_metrics.py           # F8 Genius scoring
│   ├── tcha_metrics.py             # Time-critical harm awareness
│   ├── claim_detection.py          # F1 Truth support
│   ├── refusal_accountability.py   # Refusal tracking
│   ├── crisis_handler.py           # Crisis override logic
│   ├── attestation/                # Attestation protocols
│   ├── audit/                      # Audit trail & eye adapter
│   │   └── eye_adapter.py          # @EYE integration
│   ├── eval/                       # AGI·ASI·APEX evaluators
│   │   ├── agi.py                  # AGI evaluator
│   │   ├── asi.py                  # ASI evaluator
│   │   ├── evaluate.py             # Session evaluation
│   │   └── types.py                # Evaluation types
│   ├── evidence/                   # Evidence pack & routing
│   │   ├── evidence_pack.py        # Evidence container
│   │   ├── conflict_routing.py     # Evidence router
│   │   └── routing_signal.py       # Routing signals enum
│   ├── floor_detectors/            # Floor-specific detectors
│   │   └── amanah_risk_detectors.py # F6 Amanah risk detection
│   ├── judiciary/                  # Judicial components
│   │   ├── witness_council.py      # Consensus aggregation
│   │   └── semantic_firewall.py    # Semantic filtering
│   ├── routing/                    # Routing logic
│   │   ├── prompt_router.py        # Prompt routing
│   │   └── refusal_templates.py    # Refusal templates
│   ├── stages/                     # Pipeline stages
│   │   ├── stage_000_amanah.py     # Amanah stage
│   │   └── stage_555_empathy.py    # Empathy stage
│   ├── validators/                 # Validators
│   │   └── spec_checker.py         # Spec validation
│   ├── verification/               # Verification modules
│   │   └── distributed.py          # Distributed verification
│   └── sabar_timer.py              # SABAR time governor
│
├── 🔌 integration/                  # Integration Zone (Interface)
│   ├── bridge.py                   # Integration bridge
│   ├── router.py                   # Integration router
│   ├── common_utils.py             # Common utilities
│   ├── memory_judge.py             # Memory judgment
│   ├── memory_seal.py              # Memory sealing
│   ├── memory_scars.py             # Memory scars
│   ├── memory_sense.py             # Memory sensing
│   ├── adapters/                   # LLM adapters
│   │   ├── llm_interface.py        # Base interface
│   │   ├── governed_llm.py         # Governed wrapper
│   │   ├── llm_openai.py           # OpenAI adapter
│   │   ├── llm_claude.py           # Anthropic adapter
│   │   ├── llm_gemini.py           # Google adapter
│   │   └── llm_sealion.py          # SEA-LION adapter
│   ├── api/                        # REST API
│   │   ├── app.py                  # FastAPI app
│   │   ├── middleware.py           # API middleware
│   │   └── routes/                 # API routes
│   │       ├── pipeline.py         # Pipeline endpoints
│   │       ├── federation.py       # Federation endpoints
│   │       ├── health.py           # Health checks
│   │       └── metrics.py          # Metrics endpoints
│   ├── config/                     # Configuration
│   │   └── interface_authority_config.py
│   ├── connectors/                 # External connectors
│   │   ├── litellm_gateway.py      # LiteLLM gateway
│   │   ├── failover_orchestrator.py # Failover logic
│   │   └── federation_router.py    # Federation routing
│   ├── plugins/                    # Plugin system
│   │   ├── entropy_tracker.py      # Entropy tracking
│   │   ├── floor_validator.py      # Floor validation
│   │   └── verdict_generator.py    # Verdict generation
│   ├── waw/                        # WAW federation
│   │   ├── well.py                 # WELL (Claude, ChatGPT, Copilot)
│   │   ├── wealth.py               # WEALTH (Gemini)
│   │   ├── geox.py                 # GEOX (Perplexity)
│   │   ├── prompt.py               # PROMPT (SEA-LION)
│   │   ├── rif.py                  # RIF (Reasoning)
│   │   ├── federation.py           # WAW federation
│   │   └── bridges/                # WAW bridges
│   ├── wrappers/                   # Session wrappers
│   │   └── governed_session.py     # Governed session wrapper
│   └── sealion_suite/              # SEA-LION integration
│       └── evaluator.py            # SEA-LION evaluator
│
├── 💾 memory/                       # Memory Zone (Storage)
│   ├── codex_ledger.py             # Codex ledger
│   ├── audit.py                    # Memory audit
│   ├── bands.py                    # Memory bands
│   ├── eureka_types.py             # Eureka types
│   ├── mem0_client.py              # Mem0 client
│   └── ... (memory modules)
│
├── ⚙️  system/                      # System Zone (Lifecycle)
│   ├── __init__.py                 # System exports
│   ├── __main__.py                 # CLI entry point
│   ├── apex_prime.py               # APEX PRIME verdict authority
│   ├── pipeline.py                 # Main governance pipeline
│   ├── verdict_emission.py         # Verdict formatting
│   ├── kernel.py                   # Kernel initialization
│   ├── ignition.py                 # System startup
│   ├── api_registry.py             # API registration
│   ├── runtime_manifest.py         # Runtime config
│   ├── stack_manifest.py           # Stack config
│   ├── engines/                    # AAA Engines
│   │   ├── agi_engine.py           # AGI engine
│   │   ├── asi_engine.py           # ASI engine
│   │   └── apex_engine.py          # APEX engine
│   ├── eye/                        # @EYE Sentinel
│   │   ├── core.py                 # Eye core
│   │   ├── sentinel.py             # Sentinel
│   │   ├── base.py                 # Base view
│   │   ├── floor_view.py           # Floor monitoring
│   │   ├── drift_view.py           # Drift detection
│   │   ├── shadow_view.py          # Shadow tracking
│   │   ├── genius_view.py          # Genius monitoring
│   │   ├── maruah_view.py          # Maruah (dignity) view
│   │   ├── anti_hantu_view.py      # Anti-Hantu detection
│   │   ├── version_view.py         # Version tracking
│   │   ├── trace_view.py           # Trace monitoring
│   │   └── ... (other views)
│   ├── temporal/                   # Temporal logic
│   │   ├── phoenix_logic.py        # Phoenix-72 cooling
│   │   └── freshness_policy.py     # Freshness policy
│   ├── recovery/                   # Recovery mechanisms
│   │   └── matrix.py               # Recovery matrix
│   ├── runtime/                    # Runtime logic
│   │   └── bootstrap.py            # Bootstrap
│   ├── dream_forge/                # Dream forge (lab mode)
│   │   ├── crucible.py             # Crucible
│   │   └── anvil.py                # Anvil
│   └── research/                   # Research modules
│       └── proof_of_causality.py   # Causality proofs
│
└── 🌐 mcp/                          # MCP Protocol Layer
    ├── arifos_mcp_server.py        # MCP server
    ├── well_api.py                 # WELL API
    ├── entry.py                    # MCP entry point
    └── tools/                      # MCP tools
        ├── fag_read.py             # FAG read tool
        ├── fag_write.py            # FAG write tool
        ├── tempa_read.py           # TEMPA read tool
        └── ... (other tools)
```

---

## 🔄 Import Dependency Flow

```
                         ┌─────────────────┐
                         │   __init__.py   │ ← Backward compatibility re-exports
                         └────────┬────────┘
                                  │
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
    ┌───────▼────────┐   ┌────────▼────────┐   ┌──────▼──────┐
    │   AGI Kernel   │   │   ASI Kernel    │   │ APEX Kernel │
    │  (Δ Delta)     │   │   (Ω Omega)     │   │  (Ψ Psi)    │
    └───────┬────────┘   └────────┬────────┘   └──────┬──────┘
            │                     │                    │
            └─────────────────────┼────────────────────┘
                                  │
                     ┌────────────▼────────────┐
                     │  Trinity Orchestrator   │ ← Delegates to kernels
                     │  (enforcement/)         │
                     └────────────┬────────────┘
                                  │
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
    ┌───────▼────────┐   ┌────────▼────────┐   ┌──────▼──────┐
    │  APEX PRIME    │   │   Pipeline      │   │ Integration │
    │ Verdict Auth   │   │ (system/)       │   │ Adapters    │
    │ (system/)      │   │                 │   │             │
    └────────────────┘   └─────────────────┘   └─────────────┘
```

### Import Rules (v46)

**Root-level zone files:**
- Use `..` to import from sibling zones
- Example: `enforcement/metrics.py` → `from ..system import apex_prime`

**Subdirectory files:**
- Use `...` to import from other zones
- Use `..` to import from parent zone
- Example: `enforcement/eval/asi.py` → `from ...system import apex_prime`
- Example: `enforcement/eval/asi.py` → `from ..metrics import check_truth`

---

## 🎯 Trinity AAA Data Flow

```
USER INPUT
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    INTEGRATION LAYER                        │
│  Adapters → Router → Governed Session → Evidence Pack       │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                  ENFORCEMENT LAYER                          │
│  Trinity Orchestrator → AGI/ASI/APEX Kernels                │
└─────────────────────────────────────────────────────────────┘
    │
    ├─────────────────┬─────────────────┬─────────────────┐
    │                 │                 │                 │
    ▼                 ▼                 ▼                 ▼
┌──────┐        ┌──────┐        ┌──────┐        ┌──────┐
│ AGI  │        │ ASI  │        │ APEX │        │ Meta │
│  Δ   │        │  Ω   │        │  Ψ   │        │ Gov  │
└──┬───┘        └──┬───┘        └──┬───┘        └──┬───┘
   │               │               │               │
   │ F1 Truth      │ F3 Peace²     │ F6 Amanah     │ Cross-
   │ F2 DeltaS     │ F4 κᵣ         │ F8 Witness    │ model
   │               │ F5 Ω₀         │ F9 Anti-Hantu │ checks
   │               │ F7 RASA       │               │
   │               │               │               │
   └───────────────┴───────────────┴───────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │   Floor Results        │
       │   (all 9 floors)       │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │    APEX PRIME          │
       │  Verdict Authority     │
       │  (system/apex_prime)   │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │ Verdict Emission       │
       │ → User Response        │
       └────────────────────────┘
```

---

## 🔑 Key Architectural Principles

### 1. **Orthogonality**
Each zone has a single, clear responsibility:
- **AGI** = Logic/Reasoning (Mind)
- **ASI** = Ethics/Safety (Heart)
- **APEX** = Authority/Governance (Soul)
- **Enforcement** = Constitutional checks (Police)
- **Integration** = External interfaces (Interface)
- **System** = Lifecycle management (Lifecycle)
- **Memory** = State persistence (Storage)
- **MCP** = Protocol layer (Protocol)

### 2. **Delegation Hierarchy**
```
User → Integration → Enforcement → Trinity (AGI/ASI/APEX) → APEX PRIME
```

Only **APEX PRIME** (`system/apex_prime.py`) issues `Verdict.SEAL`.
All other layers **recommend**, **evaluate**, or **route**.

### 3. **Fail-Closed Defaults**
- Missing metrics = FAIL (0.0 or -1.0)
- No evidence = VOID verdict
- Uncertainty = SABAR protocol

### 4. **Evidence-Based**
- All decisions require `EvidencePack`
- Routing based on evidence quality (`RoutingSignal`)
- Constitutional verdicts separate from routing

---

## 📊 Zone Statistics

| Zone          | Files | LoC (est) | Purpose                    |
|---------------|-------|-----------|----------------------------|
| agi/          | 4     | ~500      | AGI kernel (F1, F2)        |
| asi/          | 4     | ~600      | ASI kernel (F3-F7)         |
| apex/         | 13    | ~2000     | APEX kernel + governance   |
| enforcement/  | 50+   | ~15000    | Floor checks & validation  |
| integration/  | 40+   | ~8000     | Adapters & API             |
| memory/       | 15+   | ~3000     | State management           |
| system/       | 30+   | ~10000    | Lifecycle & engines        |
| mcp/          | 20+   | ~2000     | MCP protocol               |
| **TOTAL**     | **176+** | **~41,100** | **8 orthogonal zones** |

---

## 🎨 Visual Legend

```
🧠 AGI Kernel (Δ Delta)      - Mind/Logic/Reasoning
❤️  ASI Kernel (Ω Omega)      - Heart/Care/Ethics
👁️  APEX Kernel (Ψ Psi)       - Soul/Judge/Authority
👮 Enforcement               - Constitutional Police
🔌 Integration               - External Interface
💾 Memory                    - Storage & State
⚙️  System                    - Lifecycle Management
🌐 MCP                       - Protocol Layer
```

---

**DITEMPA BUKAN DIBERI**
*"Forged, not given" — v46 Orthogonal Architecture*

**Status:** ✅ 100% COMPLETE | **Tests:** 36/36 PASSING
**Migration:** 331 files reorganized | **Zones:** 8 canonical directories
