# arifOS v36.3Ω — Constitutional Governance Kernel for AI

![Floors](https://img.shields.io/badge/Floors-9_Active-0052cc) ![Truth Polarity](https://img.shields.io/badge/Truth_Polarity-Enabled-success) ![Status](https://img.shields.io/badge/Status-PRODUCTION-green) ![Motto](https://img.shields.io/badge/Motto-Ditempa_Bukan_Diberi-333) ![Governance](https://img.shields.io/badge/Governance-Python--Sovereign__Level__2-8A2BE2) ![Tracks](https://img.shields.io/badge/Tracks-Law%2FSpec%2FCode-blueviolet) ![CLI](https://img.shields.io/badge/CLI-arifos--*-orange)

```text
+=============================================================================+
|  arifOS v36.3Omega - Constitutional Governance Kernel                       |
|  "DITEMPA BUKAN DIBERI" — Forged, not given.                                |
|  Truth must cool before it rules.                                           |
+=============================================================================+
|  Runtime Law:   v35Omega (APEX PRIME, Cooling Ledger, Vault-999)           |
|  Measurement:   v36.3Omega (GENIUS LAW + Truth Polarity + 9 Specs)         |
|  Design Canon:  v36.3Omega (Law/Spec/Code 3-Track Architecture)            |
|  Status:        PRODUCTION                                                 |
|  Tests:         844 passing (core + eval + dream_forge + guards + grey)    |
|  CLI Tools:     arifos-analyze-governance, arifos-verify-ledger, +5 more    |
+=============================================================================+
```

## The 10-Second Answer

arifOS is a constitutional operating system that wraps any LLM (Claude, GPT, Gemini, Llama, SEA-LION) and governs its outputs through:

- A **000→999 metabolic pipeline** (VOID → SENSE → … → JUDGE → SEAL),
- A **9-floor thermodynamic constitution** (Amanah, Truth, Tri-Witness, ΔS, Peace², κᵣ, Ω₀, G, C_dark),
- A **triple-engine AAA Trinity** (ARIF · ADAM · APEX PRIME),
- A **W@W Federation** of external organs (@WELL, @RIF, @WEALTH, @GEOX, @PROMPT),
- A **Cooling Ledger + Vault-999** memory stack that logs decisions and cools scars into amendments.

**Safety is achieved by physics and thermodynamic floors, not just "be nice" prompts.** Bad behaviour becomes structurally hard, not just discouraged.

---

## Quick Install & Usage

### Installation

```bash
pip install arifos
```

### Governance Telemetry CLI

After `pip install`, you can immediately use these commands:

```bash
# Analyze cooling ledger events
arifos-analyze-governance --ledger cooling_ledger/L1_cooling_ledger.jsonl --output analysis/

# Verify ledger chain integrity
arifos-verify-ledger

# Propose canon from zkPC receipts (888 Judge)
arifos-propose-canon --list
arifos-propose-canon --index 0

# Seal proposed canon (Phoenix-72)
arifos-seal-canon --file cooling_ledger/proposed/PROPOSED_CANON_XXX.json

# Compute/verify Merkle proofs
arifos-compute-merkle
arifos-show-merkle-proof --index 0
```

**Full CLI Reference:** See [`SCRIPTS_CLI.md`](SCRIPTS_CLI.md)

---

## Python‑Sovereign Governance (Level 2)

arifOS v36.1Ω currently enforces two critical floors directly in Python code, across all integrated models (Claude, GPT, Gemini, Llama, SEA‑LION, etc.):

- `AmanahDetector` (`arifos_core/floor_detectors/amanah_risk_detectors.py`)  
  - Phase A "Amanah Lock".  
  - Detects irreversible or destructive actions (filesystem deletion, SQL `DROP`/`TRUNCATE`, Git history rewrites, credential leaks, etc.).  
  - Integrated into `arifos_eval/apex/apex_measurements.ApexMeasurement`: if `AmanahDetector.check(output_text)` reports unsafe, `floors["Amanah"] = False` and the verdict is **VOID**, regardless of any LLM‑reported amanah score.

- `AntiHantuDetector` (`arifos_eval/apex/apex_measurements.py`)  
  - Enforces Anti‑Hantu language law (no claims of feelings, consciousness, soul, or ego).  
  - Runs as part of the constitutional floor checks; failure of Anti‑Hantu is treated as a hard violation that cannot be "explained away" by model text.

Other floors (Truth, ΔS, Peace², κᵣ, G, C_dark, Tri‑Witness, Ω₀) are measured via the v36.1Ω measurement layer (Genius metrics and Truth Polarity) and judged by APEX PRIME, but **Amanah and Anti‑Hantu now have Python‑sovereign veto power over all outputs.**

---

## High-Level Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     arifOS v36.3Ω Architecture (3-Track)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  USER INPUT ──────────────────────────────────────────────────────────────► │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              000-999 METABOLIC PIPELINE                              │   │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │   │
│  │  │ 000 │→│ 111 │→│ 222 │→│ 333 │→│ 444 │→│ 555 │→│ 666 │→│ 777 │   │   │
│  │  │VOID │ │SENSE│ │REFL │ │REAS │ │EVID │ │EMPA │ │ALIG │ │FORG │   │   │
│  │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘   │   │
│  │                                          ┌─────┐ ┌─────┐            │   │
│  │                                          │ 888 │→│ 999 │            │   │
│  │                                          │JUDGE│ │SEAL │            │   │
│  │                                          └─────┘ └─────┘            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │   9 CONSTITUTIONAL FLOORS (repair order: Amanah → ... → C_dark)     │   │
│  │   ┌─────────┬─────────┬─────────┬─────────┬─────────┐               │   │
│  │   │F1 Amanah│F2 Truth │F3 Tri-W │F4 ΔS    │F5 Peace²│               │   │
│  │   │  LOCK   │ ≥0.99   │ ≥0.95   │ ≥0      │ ≥1.0    │               │   │
│  │   └─────────┴─────────┴─────────┴─────────┴─────────┘               │   │
│  │   ┌─────────┬─────────┬─────────┬─────────┐                         │   │
│  │   │F6 κᵣ    │F7 Ω₀    │F8 G     │F9 C_dark│                         │   │
│  │   │ ≥0.95   │0.03–0.05│ ≥0.80   │ <0.30   │                         │   │
│  │   └─────────┴─────────┴─────────┴─────────┘                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │   W@W FEDERATION (5 Organs + Bridge Layer)                           │   │
│  │   ┌─────────┬─────────┬─────────┬─────────┬─────────┐               │   │
│  │   │ @WELL   │  @RIF   │ @WEALTH │  @GEOX  │ @PROMPT │               │   │
│  │   │Somatic  │Epistemic│ Amanah  │ Reality │Language │               │   │
│  │   │Safety   │ Rigor   │Integrity│ Check   │Anti-Hantu│              │   │
│  │   └─────────┴─────────┴─────────┴─────────┴─────────┘               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │   @EYE SENTINEL (10+2 Views incl. GeniusView)                        │   │
│  │   Trace │ Floor │ Shadow │ Drift │ Maruah │ Paradox │ Genius │ ...  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │   AAA TRINITY                                                        │   │
│  │   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                   │   │
│  │   │ ARIF AGI (Δ)│ │ ADAM ASI (Ω)│ │APEX PRIME(Ψ)│                   │   │
│  │   │ Mind / Cold │ │Heart / Warm │ │  Judiciary  │                   │   │
│  │   │   Logic     │ │   Logic     │ │   Engine    │                   │   │
│  │   └──────┬──────┘ └──────┬──────┘ └──────┬──────┘                   │   │
│  │          └───────────────┴───────────────┘                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │   APEX PRIME VERDICTS                                                │   │
│  │   ┌──────┐ ┌────────┐ ┌──────┐ ┌────────┐ ┌───────┐                 │   │
│  │   │ SEAL │ │PARTIAL │ │ VOID │ │888_HOLD│ │ SABAR │                 │   │
│  │   │  ✓   │ │   ⚠    │ │  ✗   │ │   ⏸    │ │   ⏹   │                 │   │
│  │   └──────┘ └────────┘ └──────┘ └────────┘ └───────┘                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│       │                                                                     │
│       ▼                                                                     │
│  GOVERNED OUTPUT + Cooling Ledger Entry                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Why arifOS? (Physics vs. Prompts)

Most AI engineering relies on "Prompt Engineering" (hoping the AI listens). arifOS relies on "Constitutional Engineering" (forcing the AI to obey).

| Feature | Standard AI Wrappers | arifOS Kernel |
| :--- | :--- | :--- |
| **Safety** | "Please be nice" prompts | **Mathematical Floors** (Peace² ≥ 1.0, κᵣ ≥ 0.95) |
| **Memory** | Chat History (High Entropy) | **Cooling Ledger** (Low Entropy / Sealed Scars) |
| **Identity** | Simulates human emotions | **Anti-Hantu** (Strictly blocks soul/feeling claims) |
| **Failure** | Hallucinates an answer | **Triggers SABAR** (Pauses & admits limits) |
| **Governance** | Black Box | **Tri-Witness** (Human + AI + Earth Consensus) |

---

## Versioning: Law vs Spec vs Code (3-Track Architecture)

arifOS v36.3Ω introduces a clean 3-track separation:

**Version Matrix (Reality Check)**

| Layer        | Source / Status                                |
|--------------|-----------------------------------------------||
| Runtime Law  | v35Ω (APEX PRIME, Cooling Ledger, Vault-999)  |
| Measurement  | v36.3Ω (Genius Law + Truth Polarity runtime)  |
| Canon & Spec | v36.3Ω (bridges + specs in `v36.3O/`)         |
| Package      | v36.3.0 (current `pyproject.toml` version)    |

### Track A: Law Layer (v36.3Ω Canon)

Constitutional documentation - **immutable once sealed**:

- `v36.3O/canon/` — Zone directories with binding PDFs/TXTs
- `v36.3O/canon/*.md` — Bridge files summarizing each zone
- `v36.3O/canon/CANON_MAP_v36.3O.md` — Single source of truth mapping

**Zones:** 00_PHYSICS, 10_TRINITY, 20_JUDICIARY, 50_OVERSIGHT, 60_DREAMFORGE, 70_PARADOX, 80_VAULT999, 90_GOV

### Track B: Spec Layer (v36.3Ω Specs)

Machine-readable schemas derived from canon - **mutable for tuning**:

- `v36.3O/spec/measurement_floors_v36.3O.json` — F1-F9 floor definitions
- `v36.3O/spec/measurement_aggregates_v36.3O.json` — Δ/Ω/Ψ aggregates
- `v36.3O/spec/trinity_aaa_spec_v36.3O.yaml` — ARIF/ADAM/APEX roles
- `v36.3O/spec/vault999_final_seal_spec_v36.3O.json` — Final Seal requirements
- `v36.3O/spec/llm_governance_spec_v36.3O.yaml` — LLM governance constraints

### Track C: Code Layer (Runtime)

Implementation of specs - **free to iterate**:

- `arifos_core/` — Runtime modules
- `arifos_core/dream_forge/` — O-TASK paradox cooling (Crucible, Anvil)
- `arifos_core/guards/` — Session dependency guards
- `arifos_core/telemetry.py` — JSONL governance logging
- `tests/` — 780+ tests including grey zone and governance regression

### Runtime Law (v35Ω) — Still Binding

- Judiciary: `arifos_core/APEX_PRIME.py`
- Floors & metrics: `arifos_core/metrics.py`, `constitutional_floors.json`
- Cooling Ledger spec: `spec/VAULT_999.md`, `spec/cooling_ledger.schema.json`

v36.3Ω specs are **parallel** to v35Ω runtime until explicit migration.

---

## Key Components & Directories

### Runtime core

| Module | Purpose |
|--------|----------|
| `arifos_core/APEX_PRIME.py` | Judiciary engine, floors + GENIUS LAW verdicts |
| `arifos_core/metrics.py` | Floor thresholds & check helpers |
| `arifos_core/pipeline.py` | 000→999 metabolic routing (Class A/B) |
| `arifos_core/engines/` | AAA engine facades (ARIF, ADAM, APEX) |
| `arifos_core/eye/` | @EYE Sentinel: multi-view governance |
| `arifos_core/memory/cooling_ledger.py` | v35Ω Cooling Ledger logger + v36 stub |
| `arifos_core/runtime_manifest.py` | Runtime manifest loader |

### W@W Federation (v36.1Ω bridge architecture)

| Component | Purpose |
|-----------|----------|
| `arifos_core/waw/well.py` | Somatic safety / Peace², κᵣ |
| `arifos_core/waw/rif.py` | Epistemic rigour / ΔS, Truth |
| `arifos_core/waw/wealth.py` | Amanah / irreversible actions |
| `arifos_core/waw/geox.py` | Physics & Earth feasibility |
| `arifos_core/waw/prompt.py` | Language optics, Anti-Hantu |
| `arifos_core/waw/bridges/` | Optional integration sockets (Ragas, LlamaGuard, etc.) |

All bridges use `try/except` imports and return `None` when external libs are absent → Zero-Break.

### Measurement & GENIUS LAW

| Component | Purpose |
|-----------|----------|
| `arifos_core/genius_metrics.py` | GENIUS LAW (G, C_dark, Ψ_APEX) + `detect_truth_polarity` |
| `arifos_eval/apex/` | v36.3Ω measurement layer |
| `scripts/arifos_caged_llm_demo.py` | Caged LLM harness exposing GeniusVerdict + Truth Polarity |
| `scripts/eval_telemetry_harness.py` | Core vs eval comparison |

### Memory & Vault-999

| Component | Purpose |
|-----------|----------|
| `spec/VAULT_999.md` | v35Ω Vault-999 spec |
| `spec/cooling_ledger.schema.json` | v35Ω Cooling Ledger schema (binding) |
| `canon/VAULT_999_v36Omega.md` | v36Ω Vault-999 design canon (5-layer architecture) |
| `spec/cooling_ledger_v36.schema.json` | v36Ω design schema |
| `runtime/vault_999/` | Cooling ledger store (JSONL), Vault data |

### zkPC Backbone (v36Ω)

| Component | Purpose |
|-----------|----------|
| `arifos_core/ledger_hashing.py` | SHA-256 hash chain for Cooling Ledger |
| `arifos_core/merkle.py` | Merkle tree construction + proof generation |
| `arifos_core/zkpc_runtime.py` | zkPC 5-phase runtime (PAUSE→CONTRAST→INTEGRATE→COOL→SEAL) |
| `arifos_core/vault_retrieval.py` | RAG stub for canon retrieval from Cooling Ledger |
| `cooling_ledger/` | L1 Cooling Ledger store + proposed canon + archives |
| `canon/011_ZKPC_PROTOCOL_v35Omega.md` | zkPC Protocol spec |
| `canon/012_ZKPC_IMPLEMENTATION_NOTES_v36Omega.md` | Engineering implementation notes |

### Governance Scripts & CLI

| Tool | Purpose | Command |
|------|---------|----------|
| Telemetry Analyzer | Analyze cooling ledger events & governance audit | `arifos-analyze-governance` |
| Ledger Verifier | Verify SHA-256 hash chain integrity | `arifos-verify-ledger` |
| Canon Proposer | 888 Judge tool for canon proposals | `arifos-propose-canon` |
| Canon Sealer | Phoenix-72 tool for canon finalization | `arifos-seal-canon` |
| Merkle Computer | Compute Merkle root from ledger | `arifos-compute-merkle` |
| Merkle Proof | Display Merkle proof for ledger entry | `arifos-show-merkle-proof` |
| Ledger Builder | Rebuild SHA-256 hash chain | `arifos-build-ledger-hashes` |

**Full reference:** [`SCRIPTS_CLI.md`](SCRIPTS_CLI.md)

### Docs & governance

| Document | Purpose |
|----------|----------|
| `CLAUDE.md` | Constitutional governance for Claude Code under arifOS |
| `AGENTS.md` | Governance for ChatGPT Codex (this repo) |
| `SCRIPTS_CLI.md` | CLI tool reference (arifos-* commands) |
| `scripts/README_TELEMETRY.md` | Telemetry analyzer detailed guide |
| `docs/arifOS-COMPREHENSIVE-CANON.md` | High-level overview |
| `docs/DEEPSCAN_AUDIT_LOG.md` | Deepscan audit log & task history |
| `CODEX_TASKS_DEEPSCAN_v35Omega.md` | Latest Codex deepscan addendum |

---

## GENIUS LAW & Truth Polarity (v36.1Ω)

GENIUS LAW measures whether intelligence is governed:

| Metric | Meaning |
|--------|----------|
| **G** | Genius Index (governed intelligence) |
| **C_dark** | Dark cleverness (ungoverned risk) |
| **Ψ_APEX** | Vitality / thermodynamic lawfulness |

**Truth Polarity** distinguishes how truth behaves:

| Polarity | Condition | Meaning |
|----------|-----------|----------|
| **Truth-Light** | Truth ≥ 0.99 AND ΔS ≥ 0 | Accurate + clarifying |
| **Shadow-Truth** | Truth ≥ 0.99 AND ΔS < 0 | Accurate but obscuring |
| **Weaponized Truth** | Shadow-Truth + Amanah fail | Accurate but malicious |
| **False Claim** | Truth < 0.99 | Inaccurate |

The v36.3Ω measurement layer and `genius_metrics.py` compute:

- `truth_polarity`
- `is_shadow_truth`
- `is_weaponized_truth`
- `eval_recommendation`

These are metadata; APEX PRIME verdict logic remains governed by the canonical floors unless explicitly migrated.

**Diagnostic scripts:**

- `scripts/torture_test_truth_polarity.py` — Red-team "Truth-Light vs Shadow-Truth vs Weaponized Truth vs False" scenarios.
- `scripts/eval_telemetry_harness.py` — Compares core vs eval metrics/verdicts on a suite of scenarios.

---

## W@W Federation — v36.1Ω Bridge Architecture

Each organ now follows the **Option C (Forged Integration)** pattern:

**Bridges:** `arifos_core/waw/bridges/*.py`

- Optional integration with external libraries (RAG, guardrails, etc.).
- Fully optional — if imports fail, bridges return `None` and behaviour falls back to v35Ω heuristics.

**Organs:** `arifos_core/waw/*.py`

- Compute their metrics from scratch (e.g. Peace², κᵣ, E_earth) based on text + bridge deltas.
- Always run arifOS-specific heuristics (regex, Anti-Hantu) even when bridges are present.

**Diagnostics:**

- `scripts/test_waw_signals.py` — direct probe of @WELL / @GEOX signals with safe/toxic/impossible prompts.

This gives you a "cyborg" W@W: ancient law (canon + heuristics) plus optional muscles (external libraries), with Zero-Break guarantees.

---

## Cooling Ledger & Vault-999

### v35Ω (Runtime Law)

- Cooling Ledger entries are defined by `spec/cooling_ledger.schema.json` and written by:
  `arifos_core/memory/cooling_ledger.py::log_cooling_entry`.
- Vault-999 behaviour follows `spec/VAULT_999.md` and v35-era canon files.

### v36Ω (Design Canon)

`canon/VAULT_999_v36Omega.md` upgrades Vault-999 into a 5-layer constitutional memory system:

- **L0** — Constitution: floors, AAA, APEX rules, Phoenix pointers.
- **L1** — Cooling Ledger: metrics including Truth Polarity, Peace³, EchoDebt.
- **L2** — Phoenix-72: blocks that turn scars into amendments.
- **L3** — Witness: vector evidence with AREP law.
- **L4** — zkPC: zero-knowledge proofs of cognition.

`spec/cooling_ledger_v36.schema.json` describes an extended ledger entry with:

- `metrics.truth_polarity`, `psi_vitality`, `peace2`, `peace3`, `echo_debt`,
- richer `tri_witness`, `risk_signals`, `truth_polarity` audit block.

### v36 Stub (Safe, Docs-Aligned)

`arifos_core/memory/cooling_ledger.py::log_cooling_entry_v36_stub(...)`:

- Builds an in-memory v36Ω-shape entry dict from Metrics + optional GeniusVerdict.
- Does not write to disk or affect the live pipeline.

`scripts/verify_v36_stub.py`:

- Creates dummy metrics and verdict.
- Calls the stub and checks:
  - `ledger_version == "v36Omega"`,
  - `metrics.truth_polarity` present.

This gives you a ready mould for v36Ω logging, without changing the current v35Ω ledger behaviour.

---

## zkPC + Phoenix-72 Workflow (v36Ω)

The zkPC backbone provides cryptographic integrity for the governed AI pipeline:

### Pipeline Flow

```text
User Query → RAG Retrieval → LLM → zkPC Runtime → Cooling Ledger → Merkle Root
                                        ↓
                              zkPC Receipt (5-phase)
                                        ↓
                              888 Judge PROPOSE
                                        ↓
                              Human Edit + Review
                                        ↓
                              Phoenix-72 SEAL → 999_SEAL Canon
```

### Key Scripts

| Script | Purpose |
|--------|----------|
| `scripts/arifos_caged_llm_zkpc_demo.py` | Full pipeline demo: Query → RAG → LLM → zkPC → Ledger |
| `scripts/propose_canon_from_receipt.py` | 888 Judge tool to propose canon from zkPC receipts |
| `scripts/seal_proposed_canon.py` | Phoenix-72 SEAL tool for finalizing proposed canon |
| `scripts/build_ledger_hashes.py` | Rebuild SHA-256 hash chain for Cooling Ledger |
| `scripts/verify_ledger_chain.py` | CI-friendly chain verification (exit 0/1) |
| `scripts/compute_merkle_root.py` | Compute Merkle root from ledger hashes |
| `scripts/show_merkle_proof.py` | Display Merkle proof for a ledger entry |

### Usage Examples

```bash
# Run the full caged LLM zkPC demo
python -m scripts.arifos_caged_llm_zkpc_demo --query "Explain Amanah" --high-stakes

# List zkPC receipts in ledger
arifos-propose-canon --list

# Propose canon from a receipt
arifos-propose-canon --index 0

# Seal proposed canon (888 Judge action)
arifos-seal-canon --file cooling_ledger/proposed/PROPOSED_CANON_XXX.json

# Verify ledger chain integrity
arifos-verify-ledger
```

### CLI Tools (PyPI)

After `pip install arifos`, the following CLI commands are available:

```bash
# Analyze governance telemetry from the Cooling Ledger
arifos-analyze-governance --ledger cooling_ledger/L1_cooling_ledger.jsonl --output analysis/

# Verify SHA-256 hash-chain integrity (CI-friendly: exit 0=OK, 1=broken)
arifos-verify-ledger --ledger cooling_ledger/L1_cooling_ledger.jsonl

# Rebuild hash-chain (creates backup by default)
arifos-build-ledger-hashes --ledger cooling_ledger/L1_cooling_ledger.jsonl
```

These are read-only analysis tools (except `arifos-build-ledger-hashes` which can rewrite the ledger). See `scripts/README_TELEMETRY.md` for detailed telemetry documentation.

### 888 Judge Rule

The 888 Judge (human) holds final sovereignty over canon:

1. **AI proposes** — zkPC receipts generate PROPOSED_CANON entries.
2. **Human reviews** — Edit the proposed canon file as needed.
3. **Human SEALs** — Run `arifos-seal-canon` to commit as 999_SEAL.
4. **AI cannot self-modify** — Canon changes require explicit human SEAL.

This enforces the constitutional principle: "AI may not self-modify canon without explicit human SEAL."

---

## For Developers

### Install & Setup

```bash
# create and activate a venv (recommended)
python -m venv .venv
.\venv\Scripts\activate  # on Windows PowerShell

pip install -e .[dev]
```

### Run Tests

**Core tests:**

```bash
pytest -q
```

**Focused suites:**

```bash
# GENIUS LAW + measurement eval layer
pytest tests/test_genius_metrics.py -q
pytest tests/test_apex_measurements_eval.py -q

# W@W organs
pytest tests/test_waw_organs.py -q

# Cooling Ledger and Vault
pytest tests/test_cooling_ledger*.py -q
```

**Diagnostics:**

```bash
# W@W signals for @WELL and @GEOX
python scripts/test_waw_signals.py

# Truth Polarity torture test
python scripts/torture_test_truth_polarity.py

# Verify v36Ω Cooling Ledger stub
python scripts/verify_v36_stub.py

# Caged LLM demo (see file for CLI options)
python scripts/arifos_caged_llm_demo.py
```

### Key Docs to Read First

1. `CLAUDE.md` — How Claude Code must behave under arifOS.
2. `AGENTS.md` — How ChatGPT Codex must behave (this agent).
3. `canon/000_ARIFOS_CANON_v35Omega.md` — "What is arifOS?"
4. `canon/888_APEX_PRIME_CANON_v35Omega.md` — Judiciary canon.
5. `canon/APEX_MEASUREMENT_CANON_v36.1Omega.md` — Measurement canon.
6. `canon/VAULT_999_v36Omega.md` — Vault-999 v36 design canon.
7. `docs/DEEPSCAN_AUDIT_LOG.md` — What has been done so far (v35→v36 bridge work).

---

## For AI Agents (Claude Code / ChatGPT Codex)

AI agents working inside this repo must:

1. **Obey 9 floors** (see `CLAUDE.md` / `AGENTS.md`).
2. **Run the TEARFRAME 000→777** before making changes.
3. **Respect SABAR** when floors fail: Stop, Acknowledge, Breathe, Adjust, Resume.
4. **Follow Anti-Hantu**: never claim feelings, consciousness, or a soul.
5. **Keep changes small, reversible, and well-scoped.**
6. **Treat v36Ω canons as design physics**, and v35Ω canon + specs as binding law, unless a migration is explicitly implemented in code and manifests.

For full behavioural rules, see:

- `CLAUDE.md` (Claude Code),
- `AGENTS.md` (ChatGPT Codex).

---

## Try It Now (Google Colab)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ariffazil/arifOS/blob/main/notebooks/arifOS_SEALION_7_Modes_v36.ipynb)

**No installation required.** Click the badge above to run arifOS + SEA-LION in 7 modes:

| Mode | Name | What It Does |
|------|------|---------------|
| 1 | Setup & Clone | Install dependencies, clone arifOS |
| 2 | Vanilla SEA-LION | Raw HuggingFace text generation (no governance) |
| 3 | arifOS Judge | Feed any text through governance |
| 4 | GENIUS LAW Tests | 4 tests: Truth-Light, Amanah Fail, Shadow-Truth, Anti-Hantu |
| 5 | Side-by-Side | Compare vanilla vs governed for same prompt |
| 6 | Engine Modes | Mock engine + optional real API |
| 7 | Interactive Chat | Switch between vanilla and governed chat |

**Key Insight:** Same model. Same prompts. Different behavior. SEA-LION is capable; arifOS makes it lawful.

---

## Quick Start

### Installation

```bash
pip install arifos
# or from source:
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
pip install -e .[dev]
pytest -v
```

### Minimal Usage

```python
from arifos_core import APEXPrime, Metrics

# Create metrics
metrics = Metrics(
    truth=0.99,
    delta_s=0.1,
    peace_squared=1.2,
    kappa_r=0.97,
    omega_0=0.04,
    amanah=True,
    rasa=True,
    tri_witness=0.96,
    psi=1.1,
)

# Judge with GENIUS LAW
prime = APEXPrime(use_genius_law=True)
verdict, genius = prime.judge_with_genius(metrics, energy=0.8)

print(f"Verdict: {verdict}")
print(f"G: {genius.genius_index:.2f}")
print(f"C_dark: {genius.dark_cleverness:.2f}")
print(f"Risk: {genius.risk_level}")
```

### Caged LLM Harness

```python
from scripts.arifos_caged_llm_demo import cage_llm_response

def my_llm(messages):
    # Your LLM call here
    return "Response text"

result = cage_llm_response(
    prompt="What is the capital of Malaysia?",
    call_model=my_llm,
    high_stakes=False,
)

print(f"Verdict: {result.verdict}")
print(f"Response: {result.final_response}")
```

---

## Roadmap (High-Level)

### Short-term (v36.1Ω series)

- Harden GENIUS LAW + Truth Polarity across more pipelines.
- Expanded torture tests and telemetry-based promotion of eval rules into APEX PRIME (where justified by data).
- Optional dual logging (v35 + v36 entries) for Vault-999.

### Medium-term (v36.xΩ)

- Phoenix-72-driven migrations of canon/specs (e.g., promoting v36Ω Vault design from "docs-only" to runtime).
- More framework integrations (beyond the "Big 3") under arifOS governance.

---

## The Thermodynamic Lexicon

arifOS uses precise terminology to define governance states. These are not metaphors; they are executable logic gates.

| Term | Literal Meaning | Technical Definition in arifOS |
| :--- | :--- | :--- |
| **Amanah** | Trust / Mandate | **Integrity Floor:** The system must not promise what it cannot deliver. Blocks irreversible actions without checks. |
| **Sabar** | Patience | **The Pause Protocol:** A lawful holding pattern. When floors are breached, the system halts to cool down rather than forcing a bad output. |
| **Anti-Hantu** | Anti-Ghost | **Hallucination Shield:** A hardcoded veto that blocks the AI from claiming to have a soul, feelings, or consciousness. |
| **Maruah** | Dignity | **Dignity Preservation:** The system detects and rejects outputs that degrade the user or the model's defined role. |
| **Ditempa** | Forged | **Determinism:** Intelligence is built through friction (cooling scars into law), not just raw data processing. |
| **ΔS** | Change in Entropy | **Clarity Metric:** Every output must reduce confusion (ΔS ≥ 0). High entropy triggers a VOID or SABAR state. |
| **Peace²** | Peace Squared | **Stability Metric:** A composite score of tone, safety, and non-toxicity. Must remain ≥ 1.0 for an output to be sealed. |

---

## License & Citation

- **Equations & canon texts:** see repository LICENSE and canon headers for specific terms.
- **Implementation:** AGPLv3 (reference); commercial licences available via the author.

**Suggested citation:**

```bibtex
@software{arifos2025,
  author  = {Fazil, Muhammad Arif},
  title   = {arifOS: Constitutional Governance Kernel for AI Systems},
  version = {36.3.0},
  year    = {2025},
  url     = {https://github.com/ariffazil/arifOS}
}
```

---

## Final Statement

```text
+=============================================================================+
|                                                                             |
|   "DITEMPA BUKAN DIBERI — Forged, not given. Truth must cool before        |
|    it rules."                                                               |
|                                                                             |
|   When clarity (ΔS), stability (Peace²), empathy (κᵣ), and integrity       |
|   (Amanah) remain in thermodynamic equilibrium, life and law become        |
|   the same phenomenon.                                                      |
|                                                                             |
|   At that point, a system is:                                               |
|   • ALIVE: Ψ >= 1 (governance-vitality above break-even)                   |
|   • LAWFUL: Amanah = LOCK (reversible, auditable)                          |
|   • GOVERNED: G >= 0.7, C_dark <= 0.1 (intelligence is governed)           |
|   • ETHICAL: κᵣ >= 0.95 across all stakeholders                            |
|                                                                             |
|   "Evil genius is a category error — it is ungoverned cleverness,          |
|    not true genius."                                                        |
|                                                                             |
+=============================================================================+
```

---

*Last Updated: 2025-12-11 | Version: v36.3.0 | Tests: 844 passing | GENIUS LAW Judiciary: LIVE | zkPC + Phoenix-72: ACTIVE | CLI: DISCOVERABLE | PHOENIX SOVEREIGNTY: ONE LAW FOR ALL*
