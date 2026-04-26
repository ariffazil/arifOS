# K007 — LLM / Deterministic Boundary Doctrine

**Plan ID:** `PLAN-12a849b7db4c4b72`  
**Effective:** 2026-04-26  
**Supersedes:** All prior internal LLM usage guidelines  
**Governance:** Constitutional Tier — Immutable once sealed

---

## 1. Purpose

This doctrine establishes the **irreducible separation** between the LLM-based interpretive layer and the deterministic execution substrate. Intelligence (LLM) advises; authority (deterministic core) decides. No LLM component may influence irreversible state, audit integrity, or routing authority.

---

## 2. Architectural Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERPRETIVE LAYER (LLM)                  │
│                                                             │
│  333_MIND    — Symbolic reasoning, plan generation         │
│  444_REPLY   — Human-facing composition, tone control       │
│  666_HEART   — Ethical critique, empathy modeling           │
│  888_JUDGE   — Constitutional interpretation (verdict emit)  │
│  111_SENSE   — Semantic parsing of observations             │
│                                                             │
│  SEA-LION / Ollama  ← Wisdom quote interpreter             │
└─────────────────────────────────────────────────────────────┘
                           │ ↑ quotes only
                           │ ↑ interpretation
                           ↓
┌─────────────────────────────────────────────────────────────┐
│               DETERMINISTIC SUBSTRATE (Non-LLM)             │
│                                                             │
│  000_INIT    — Identity binding, constitutional hash        │
│  999_VAULT   — Immutable ledger, cryptographic sealing       │
│  777_OPS     — Telemetry, thermodynamic metrics             │
│  010_FORGE   — System mutation, builds, deployments         │
│  555_MEMORY   — Storage layer (not semantic recall)         │
│  444_KERNEL  — Deterministic routing, stage enforcement     │
│                                                             │
│  quote_ledger     ← Append-only, cryptographically sealed   │
│  context_safety    ← Fail-closed validation gate             │
└─────────────────────────────────────────────────────────────┘
```

**Invariant:** Output of the Interpretive Layer is **advisory only**. The Deterministic Substrate **must** validate, reject, or modify any advisory before it affects system state.

---

## 3. Components — LLM Interpretive Layer

### 3.1 Scope

| Stage | Component | LLM Role |
|-------|-----------|----------|
| 333 | `arif_mind_reason` | Axiom tracing, plan generation, critique |
| 444 | `arif_reply_compose` | Tone control, semantic clarity, citation injection |
| 666 | `arif_heart_critique` | Empathy modeling, risk narrative framing |
| 888 | `arif_judge_deliberate` | Constitutional interpretation, verdict deliberation |
| 111 | `arif_sense_observe` | Semantic parsing of observations |

### 3.2 Wisdom Quote Interpreter (SEA-LION / Ollama)

The quote interpretation layer (`sea_lion_interpreter.py`) is the **only** LLM component that touches wisdom quotes, and it is constrained:

- **May NOT** invent quotes, authors, or alter quote text
- **May ONLY** select from candidate quotes supplied by `retrieve_witnesses()`
- **Must** pass `validate_interpretation_safety()` before output is accepted
- **Fallback chain:** SEA-LION (production `api.sea-lion.ai`) → Ollama (`qwen2.5:7b`) → deterministic `fallback_interpret()`

---

## 4. Components — Deterministic Substrate

### 4.1 Scope

| Stage | Component | Deterministic Guarantee |
|-------|-----------|------------------------|
| 000 | `arif_session_init` | Identity binding, constitutional hash anchoring — no LLM |
| 999 | `arif_vault_seal` | Append-only ledger, Merkle chaining — no LLM |
| 777 | `arif_ops_measure` | Thermodynamic metrics, entropy — no LLM |
| 010 | `arif_forge_execute` | System mutation, builds — no LLM (execution layer) |
| 555 | `arif_memory_recall` | Storage layer (semantic recall goes through MIND) |
| 444 | `arif_kernel_route` | Stage routing, policy enforcement — no LLM |

### 4.2 Safety Gates

All LLM output passes through `validate_interpretation_safety()` before affecting any downstream component:

```
LLM output
    ↓
validate_interpretation_safety()
    ├── FAIL: selected_quote_id not in candidate_quotes  → HOLD
    ├── FAIL: quote text mismatch ledger                 → HOLD
    ├── FAIL: author mismatch ledger                     → HOLD
    ├── FAIL: risk_level HIGH/CRITICAL + human_required=false → HOLD
    └── PASS → safe_output propagated
```

---

## 5. F02 + F11 Compliance Proof

### F02 — TRUTH: No Fabrication

| Risk | Mitigation |
|------|------------|
| LLM invents a quote | `context_safety.py` — quote_id must be in `candidate_quotes` AND ledger |
| LLM fabricates author | Ledger lookup validates author field |
| LLM alters quote text | Exact string comparison against ledger |
| LLM claims authority for irreversible action | `human_decision_required=true` gate for HIGH/CRITICAL/IRREVERSIBLE |

**Proof:** The only quotes that may be selected are those pre-approved in `quote_ledger.py`. No LLM can introduce a quote that does not exist in the ledger.

### F11 — AUTH: Identity and Integrity Boundary

| Risk | Mitigation |
|------|------------|
| LLM influences vault sealing | VAULT core is pure deterministic — no LLM import in `vault.py` |
| LLM overrides KERNEL routing | Routing is pure policy enforcement — no LLM path in `kernel.py` |
| LLM modifies OPS telemetry | OPS returns fixed metrics from system calls — no LLM |
| LLM spoofs INIT identity binding | INIT uses cryptographic hash — no LLM |
| LLM bypasses FORGE execution controls | FORGE enforces judge_state_hash + vault_entry_id — no LLM |

**Proof:** The deterministic substrate has **zero import dependencies** on LLM components. Code audit of `arifosmcp/core/vault.py`, `arifosmcp/core/kernel.py`, `arifosmcp/core/ops.py`, `arifosmcp/core/init.py` confirms no imports of `sea_lion_interpreter`, `ollama`, or any LLM client module.

---

## 6. Ledger Anchoring Constraint

All wisdom quote selection **must** satisfy:

1. Quote exists in `WISDOM_REGISTRY` (`wisdom_quotes.py`)
2. Quote is marked `allow_use=True`
3. Quote has `source_status != "uncertain"`
4. Quote is in `quote_ledger.py` approved set
5. `retrieve_witnesses()` scored and ranked deterministically
6. LLM selects from top-k candidates only

**No quote may be selected outside this chain.**

---

## 7. Governance Boundary Enforcement Invariant

For all `context_witness` outputs:

```
human_decision_required = true  IF  risk_level ∈ {high, critical, irreversible}
```

This is enforced by `_apply_governance_boundary()` in `context_witness.py` — a deterministic function that **cannot be overridden by LLM output**.

---

## 8. Forbidden Patterns

| Forbidden | Reason | Floor |
|-----------|--------|-------|
| LLM directly writing to VAULT999 | Breaks append-only integrity | F02, F11 |
| LLM generating judge_state_hash | Breaks cryptographic chain | F11 |
| LLM bypassing kernel routing | Breaks stage enforcement | F11 |
| LLM modifying OPS metrics | Breaks auditability | F02 |
| LLM fabricating quote or author | Breaks wisdom ledger integrity | F02, F03 |
| LLM overriding human_decision_required | Breaks sovereignty | F13 |

---

## 9. Review and Amendment

- Amendments require a `SEAL` verdict from `888_JUDGE`
- This doctrine is **immutable once sealed** in `000/ROOT/K007_LLM_BOUNDARIES.md`
- Any future LLM integration must pass the F02 + F11 compliance proof above

---

**DITEMPA BUKAN DIBERI — Intelligence advises; authority decides.**
