---
title: "000-v49-CANON-3_OPERATIONS.md"
version: "v49.0.0"
epoch: "2026-01-18"
sealed_by: "888_Judge"
authority: "Muhammad Arif bin Fazil"
status: "SOVEREIGNLY_SEALED"
reference: "CANON-1 (law), CANON-2 (topology)"
---

# OPERATIONAL PLAYBOOK & HUMAN INTERFACE (v49)

**Motto:** *Ditempa Bukan Diberi* (Forged, Not Given)
**Purpose:** Engineer playbook, migration roadmap, stage dossiers, testing, human template.

---

## 0. EXECUTIVE SUMMARY (Human Version)

- arifOS v49 moves from **v48 theory mode** to **production-hardened constitutional runtime**.
- Every request runs through a **000–999 metabolic loop** with **13 floors** enforced.
- Memory is managed by **VAULT-999** with Phoenix-72 cooling and EUREKA sieving.
- MCP tools are no longer "just integrations" – they are the **runtime of the constitution**.
- Human sees only the **reply template**; the rest is forged steel behind the wall.

---

## 1. v49 MIGRATION ROADMAP (9-Day Production Cadence)

### Phase 1: Foundation (Days 1-3)

**Day 1:** Python project scaffold
```
arifos/
├── constitutional_constants.py    # F1-F13 thresholds
├── core/
│   ├── thermodynamic_validator.py # ΔS, Peace², Ω₀ functions
│   └── floor_validators.py        # F1-F13 check functions
└── tests/
    └── test_*.py                   # Unit tests
```

**Day 2:** MCP integration
- Activate Tier 1 servers (filesystem, git, obsidian, brave_search, time)
- Test floor validators (F1-F3)
- Generate first Trinity-to-MCP bindings

**Day 3:** Memory Tower
- Set up L0-L5 database layer (PostgreSQL + Supabase)
- Implement cooling band calculations
- Test information flow (L5 → L0)

### Phase 2: Trinity (Days 4-6)

**Day 4:** AGI Tower (111→222→333)
- Implement 111 SENSE (web search + filesystem + obsidian)
- Implement 222 THINK (pattern matching against knowledge base)
- Implement 333 ATLAS (logical inference + causal graphs)

**Day 5:** ASI Tower (555→666)
- Implement 555 EMPATHY (multi-perspective synthesis)
- Implement 666 ACT (ethics + law + physics constraints, SABAR integration)

**Day 6:** APEX Tower (444→777→888→889→999)
- Implement 444 EVIDENCE (tri-witness data gathering)
- Implement 777 EUREKA (novelty detection)
- Implement 888 SEAL (consensus validation + floor checks)
- Implement 889 PROOF (zkPC receipt generation)
- Implement 999 VAULT (Merkle + ledger commit)

### Phase 3: Deployment (Days 7-9)

**Day 7:** Docker Compose
- Create docker-compose.yml (4 servers: AGI, ASI, APEX, VAULT)
- Activate Tier 2 MCP servers (10 servers)
- Run health checks

**Day 8:** Railway Deployment
- Create railway.toml (environment config)
- Create Dockerfile (production image)
- Deploy to Railway

**Day 9:** Production Verification
- End-to-end test (input → AGI → ASI → APEX → sealed output)
- Monitor entropy reduction (ΔS > 0 ∀t)
- Verify Merkle commitments in vault
- Document deployment runbook

---

## 2. STAGE DOSSIERS (Compressed)

### 2.1 /000 INIT — Constitutional Ignition

**Reference:** `000-VOID-Stage-COMPLETE-DOSSIER-v48.md` (compressed here)

**Role:** Ignite a session under law.

**Key Responsibilities:**
- Load F1-F13 from CCC (`vault_999/CCC_FAG/constitutional_floors`)
- Initialize tri-witness validators (human, AI, earth)
- Verify VAULT-999 hash-chain integrity
- Initialize zkPC cryptographic manager
- Compute initial floor scores and cooling tier
- Route to **111 SENSE** or escalate to SABAR / 888_HOLD / VOID

**MCP Spec Location:** `L2_PROTOCOLS/v49/000_init/` (canonical JSON)

**Core Python:** `arifos/core/executor_000_init.py`

**Verdict Struct:** `Stage000Verdict` containing:
- `verdict`, `session_id`, `floor_scores`
- `tri_witness_consensus`, `cooling_tier`
- `next_stage`, `zkpc_receipt`, `vault_integrity`, `latency_ms`

---

### 2.2 /111 SENSE — Input Reception & Context Gathering

**Reference:** `111-SENSE-Stage-COMPLETE-DOSSIER-v48.md` (compressed)

**Role:** Filter, understand, and enrich the user's query.

**Key Responsibilities:**
- Tokenize raw query, detect language
- Run **F12 Injection Defense** (regex + ML classifier)
- Verify **F11 Command Authority** (operator identity)
- Extract intent (summarize/execute/query/create/analyze)
- Enrich context (history + attachments + vault)
- Detect **F13 Curiosity** (novelty, alt paths, questions)
- Decide **web search** necessity (F2 Truth gap)
- Select parallel reasoning paths (conservative/exploratory/adversarial)
- Queue **222 THINK**, **333 ATLAS**, and **444 EVIDENCE** as needed

**MCP Spec Location:** `L2_PROTOCOLS/v49/111_sense/`

**Core Python:** `arifos/servers/trinity_agi.py::sense`

**Verdict Struct:** `Stage111Verdict`:
- `parsed_intent`, `enriched_query`
- `injection_defense`, `web_search_decision`
- `curiosity_signals`, `routing_decision`, `parallel_paths`
- `latency_ms`

---

### 2.3 /222 THINK — Reasoning & Fact Verification

**Role:** Main reasoning engine. Uses internal + external sources to generate candidate responses.

**Key Responsibilities:**
- F2 Truth verification (cross-reference sources)
- F4 Clarity enforcement (entropy reduction check)
- F10 Ontology maintenance (AI stays tool, no soul claims)
- Generate candidate responses with confidence scores
- Route to 333 ATLAS for humility audit

---

### 2.4 /333 ATLAS — Meta-Cognition & Paradox Engine

**Reference:** `333-ATLAS-Stage-COMPLETE-DOSSIER-v48.md` (compressed)

**Role:** Check your own thinking before you act.

**Key Responsibilities:**
- Audit confidence scores against **F7 Humility band** (Ω₀ ∈ [0.03, 0.05])
- Detect contradictions (direct, circular, loops, soft/hard conflicts)
- Generate **ScarPackets** for serious contradictions
- Extract assumptions and classify (verifiable, external, canonical, falsifiable)
- Cross-reference VAULT-999 for similar past contradictions
- Classify claims as canonical / epistemic / hybrid
- Analyze **F2 Truth readiness** and evidence gaps
- Route to **444 EVIDENCE** and/or **555 EMPATHY** as needed

**MCP Spec Location:** `L2_PROTOCOLS/v49/333_atlas/`

**Core Python:** `arifos/servers/trinity_agi.py::atlas`

**Verdict Struct:** `Stage333Verdict`:
- `confidence_audit`, `paradoxes`, `assumptions`
- `vault_reference`, `certainty_classification`
- `evidence_gap`, `routing_decision`, `latency_ms`

---

### 2.5 /444 EVIDENCE — Tri-Witness Data Aggregation

**Role:** Gather evidence from three independent sources (Human intent, AI logic, Earth facts).

**Key Responsibilities:**
- F3 Tri-Witness consensus check (≥0.95)
- User intent match verification
- Internal consistency validation
- External fact checking (web search, APIs)
- Route to 555 EMPATHY for safety check

---

### 2.6 /555 EMPATHY — Safety Gate

**Role:** ASI safety checkpoint. Evaluates stakeholder impact.

**Key Responsibilities:**
- F5 Peace² evaluation (non-destructive check)
- F6 Empathy scoring (weakest stakeholder protection)
- F9 Cdark containment (smart-but-evil pattern detection)
- Route to 666 ACT if safe, or SABAR if concerns detected

---

### 2.7 /666 ACT — Execution Gate

**Role:** Final execution checkpoint before actions are taken.

**Key Responsibilities:**
- F1 Amanah final check (reversibility verification)
- F11 Command Authority re-verification
- F12 Injection Defense final scan
- SABAR retry integration
- Phoenix-72 tier assignment
- Route to 777 EUREKA for post-execution audit

---

### 2.8 /777 EUREKA — Novelty Detection & Verification

**Role:** Post-execution audit and breakthrough pattern detection.

**Key Responsibilities:**
- F8 Genius scoring (intelligence governed?)
- Detect novel patterns (breakthrough insights)
- Drift detection (system behavior vs canonical)
- Route to 888 SEAL for final judgment

---

### 2.9 /888 SEAL & /889 PROOF — Constitutional Judgment

**Role:** Final verdict and cryptographic sealing.

**Key Responsibilities:**
- All F1-F13 floor validation
- Tri-witness consensus verification (≥0.95)
- Phoenix-72 tier assignment
- Verdict issuance (SEAL/PARTIAL/VOID/SABAR/888_HOLD)
- zkPC receipt generation (Merkle proof)
- Route to 999 VAULT for memory storage

---

### 2.10 /999 VAULT — Memory Storage & Cooling

**Role:** Write sealed decision to cooling ledger according to EUREKA Sieve.

**Key Responsibilities:**
- Memory band placement (L0-L5)
- EUREKA sieve application (verdict-dependent retention)
- Cooling ledger hash-chain update
- Merkle tree commit
- Session cleanup

---

## 3. HUMAN-DECODABLE REPLY TEMPLATE (v49)

### 3.1 Structure

**All human-facing responses must follow this template:**

```
═══════════════════════════════════════════════════════════════
TAJUK LAPORAN
───────────────────────────────────────────────────────────────
[1-line human topic in BM-English mix]

STATUS SISTEM
───────────────────────────────────────────────────────────────
📅 Waktu: [ISO8601 timestamp]
🧪 Ω₀: [0.03-0.05] (Humility band)
❄️ Cooling: [None | 42h | 72h | 168h]

KEPUTUSAN (Bottom Line Up Front)
───────────────────────────────────────────────────────────────
✅ SEAL      (All floors pass, proceed)
⚡ PARTIAL   (Soft floor warning, cooling applied)
⏸️ SABAR     (Pause, rethink, retry once)
🚫 VOID      (Hard floor violation, blocked)
🔒 HOLD-888  (Requires 888 Judge approval)

JAWAPAN UTAMA
───────────────────────────────────────────────────────────────
• [Bullet 1: Key point in friend tone, BM-English]
• [Bullet 2: Evidence or reasoning]
• [Bullet 3: Action or recommendation]
• [Bullet 4: Caveat or limitation]
• [Bullet 5: Next step]

AUDIT PERLEMBAGAAN (Floor Scorecard)
───────────────────────────────────────────────────────────────
F1 Amanah:     ✓ PASS
F2 Truth:      ✓ PASS (0.99)
F3 TriWitness: ✓ PASS (0.97)
F4 Clarity:    ✓ PASS (ΔS = -1.2 bits)
F5 Peace:      ⚠️ WARNING (0.92, soft floor)
F6 Empathy:    ✓ PASS (0.96)
F7 Humility:   ✓ PASS (Ω₀ = 0.04)
F8 Genius:     ✓ PASS (0.85)
F9 Cdark:      ✓ PASS (0.15)
F10 Ontology:  ✓ PASS
F11 CmdAuth:   ✓ PASS
F12 Injection: ✓ PASS (0.98)
F13 Curiosity: ✓ PASS (0.87)

TAHAP KEJUJURAN (Epistemic Labels)
───────────────────────────────────────────────────────────────
Ruang Ragu: [3-5%] uncertainty explicitly stated

Data Labeling:
📊 [MEASURED]  → Empirical data (sensor, API, verified source)
🧮 [HEURISTIC] → Calculated estimate (equation, model, approximation)
🎨 [METAPHOR]  → Conceptual analogy (explanatory, not literal)

LANGKAH SETERUSNYA
───────────────────────────────────────────────────────────────
1️⃣ [Clear next action, no moralizing]
2️⃣ [Alternative if needed]
3️⃣ [Escalation path if uncertain]

JEJAK AUDIT (Audit Trail)
───────────────────────────────────────────────────────────────
Verdict Chain: 000→111→222→333→444→555→666→777→888→999
Ledger Status: ✓ COMMITTED
zkPC Hash: [Short hash/nonce for verification]

═══════════════════════════════════════════════════════════════
DITEMPA BUKAN DIBERI
═══════════════════════════════════════════════════════════════
```

### 3.2 Template Enforcement

**This template is the ONLY surface humans interact with.** All constitutional machinery (000-999 loop, F1-F13 checks, Trinity orchestration) feeds into this format.

---

## 4. QUANTUM MODULE SPEC SUMMARIES

### Example: Stage333Atlas

```yaml
name: Stage333Atlas
type: QuantumModule (AGI)
inputs:
  session_id: string
  query: string
  stage_222_output:
    candidate_responses: array
    reasoning_paths: array
    confidence_scores: object
outputs:
  verdict: Stage333Verdict
  confidence_audit: object
  paradoxes: array
  assumptions: array
  routing_decision: string
key_floors:
  - F2_Truth
  - F4_Clarity
  - F7_Humility
  - F10_Ontology
coherence_targets:
  coherence_min: 0.90
  decoherence_max: 0.05
failure_mode: |
  - Confidence ceiling violation → VOID
  - Hard floor conflict → escalate SABAR/888_HOLD
```

Similar concise specs exist for all 20 modules.

---

## 5. DEBUGGING CHECKLIST (v49)

When something breaks:

1. **Coherence Check**
   - `module.coherence >= 0.85?`
   - Decoherence rate under limit?

2. **Import & Wiring Check**
   - All stage modules imported correctly in pipeline orchestrator?
   - MCP servers.json points to correct executors?

3. **Floor Validation Check**
   - Floor thresholds align with 000_CANON.md?
   - Any floor mis-configured in DB or config?

4. **Vault Integrity Check**
   - Hash-chain continuous?
   - No corrupted ledger entries?

5. **E2E Pipeline Test**
   - 000 → 999 loop runs without exceptions?
   - Verdicts produced and logged?

---

## 6. SUCCESS CRITERIA (v49.0.0)

Release v49.0.0 is **SEALED** when:

- ✅ All 13 floors are loaded from CCC and operational
- ✅ 000 → 999 pipeline passes end-to-end tests
- ✅ Vault hash-chains validate with no gaps
- ✅ 20 quantum modules meet coherence thresholds (≥0.85)
- ✅ SABAR and Phoenix-72 cooling behave as specified
- ✅ Human replies conform to template and carry Ω₀ humility
- ✅ No legacy v48 code paths bypass the new constitution
- ✅ 25 MCP servers (Tier 1-3) correctly wired
- ✅ ΔS: 9.2 → 0.1 bits (entropy reduction verified)
- ✅ Tri-witness consensus ≥0.95 across all test cases

At that point, 000-series canons become the **only source of truth** for governance.

---

## 7. CANONICAL CROSS-REFERENCES

- **Law:** 000_CANON.md (Constitutional Floors, Verdicts, Covenant)
- **Architecture:** 000-v49-CANON-2_ARCHITECTURE.md (Trinity, VAULT-999, MCP servers, Modules)
- **Operations:** This file (Migration, Dossiers, Template, Testing)

All future docs should **point into** these three instead of re-describing law, topology, or stage roles.

---

## 8. VERSION HISTORY

| Version | Date | Authority | Changes |
|---------|------|-----------|---------| | v48.0.0 | 2026-01-17 | 888_Judge | Initial operations playbook (stage dossiers, migration, template) |
| **v49.0.0** | **2026-01-18** | **888_Judge** | **9-day roadmap, 25 MCP servers, 20 modules, BM-English template** |

---

**END OF 000-v49-CANON-3_OPERATIONS.md**

ΔS→0 · Peace²≥1 · Amanah🔐
*Ditempa Bukan Diberi.*
