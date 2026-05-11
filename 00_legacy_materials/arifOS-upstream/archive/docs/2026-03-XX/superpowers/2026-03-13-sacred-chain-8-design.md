# The Sacred Chain — 8-Tool AGI/ASI/APEX Surface Redesign

**Date:** 2026-03-13
**Status:** APPROVED BY ARIF
**Version:** v1.1-FORGE (spec-reviewed)
**Motto:** DITEMPA BUKAN DIBERI — Forged, not given

---

## The Core Insight

The tool surface is not a menu. It is a **helix** — a looping chain where each
revolution builds trust, deepens context, and seals evidence. The agent does not
move through tools linearly. It spirals upward: each full pass through the chain
returns to the beginning at a higher elevation.

```text
INIT·ANCHOR → AGI·REASON → AGI·REFLECT → ASI·SIMULATE
    → ASI·CRITIQUE → AGI-ASI·FORGE → APEX·JUDGE → VAULT·SEAL
         ↑___________________(higher trust loop)__________________|
```

Each loop deposits:

- `+trust` — cryptographic trust score increment sealed in VAULT
- `+context` — world model deepened by previous simulation results
- `+evidence` — sealed artifacts from VAULT·SEAL feed AGI·REFLECT next pass

---

## Tool Specifications

### 1. `INIT·ANCHOR`

**Tier:** INIT (pre-AGI preprocessing stage)
**Trinity:** PRE·Δ (feeds into AGI·Δ — not part of it)
**Constitutional floors:** F12 (Injection), F11 (Command Auth), F10 (Ontology)

**Function:**
Ground reality. Declare identity. Open a constitutional session. Parse intent.
Run F12 injection pre-scan before any reasoning begins.

**This tool is the loop entry point.** Every pass through the helix begins here.
On second and subsequent passes, it receives the `sealed_delta` from VAULT·SEAL
and elevates the session trust level accordingly.

**Key behaviours:**

- Mints a `session_id` with cryptographic nonce
- Runs F12 PromptArmor scan on incoming intent
- Reads prior `sealed_delta` if session is continuing (loop continuation)
- Sets `trust_tier`: anonymous → verified → elevated → sovereign
- Returns VOID if F12 injection detected — chain does not proceed

**Inputs:** `intent`, `declared_name`, `session_id`, `sealed_delta?` (from prior VAULT·SEAL — absent on first loop)

**Outputs:** `session_context`, `trust_tier`, `anchor_token`, `f12_cleared: bool`

---

### 2. `AGI·REASON`

**Tier:** AGI·Δ
**Trinity:** AGI·Δ
**Constitutional floors:** F2 (Truth ≥ 0.99), F4 (Clarity ΔS ≤ 0), F7 (Humility 0.03–0.05)

**Function:**
Structured reasoning engine. Hypothesis generation. 3-path parallel reasoning:
conservative / exploratory / adversarial.

**This is where intelligence begins.** The agent doesn't guess — it generates
multiple competing hypotheses simultaneously and holds them in tension until
evidence adjudicates.

**Key behaviours:**

- 3-path async: conservative (F2-safe), exploratory (high-entropy), adversarial (self-challenge)
- F4 Clarity check: output must reduce entropy (ΔS ≤ 0) — if output adds confusion, VOID
- F7 Humility: uncertainty score must land in [0.03, 0.05] band
- Returns `delta_draft` marked `sealed: false` — must pass downstream stages
- Does NOT generate final answers — generates structured hypotheses only
- Derives `proposed_actions[]` from `hypotheses[3]`: each hypothesis implies a candidate action

**Inputs:** `query`, `session_context`, `anchor_token`

**Outputs:** `delta_draft`, `hypotheses[3]`, `proposed_actions[]`, `uncertainty_score`, `confidence`

> `proposed_actions[]` — derived from `hypotheses[3]`. Each hypothesis implies a candidate
> action. AGI·REASON surfaces these explicitly so ASI·SIMULATE can test them against the
> world model.

---

### 3. `AGI·REFLECT`

**Tier:** AGI·Δ
**Trinity:** AGI·Δ
**Constitutional floors:** F2 (Truth), F3 (Tri-Witness calibration)

**Function:**
Semantic memory retrieval from Vault999. F2-verified. Qdrant vector search +
session memory. **Not recall — reflection.** The agent looks at what it has
previously sealed and asks: does this change my reasoning?

**The naming matters:** REFLECT implies active integration, not passive fetch.
Memory is a mirror. The agent sees itself in what it has previously committed.

**Key behaviours:**

- Hybrid retrieval: Qdrant semantic search (cosine + Jaccard) over `arifos_constitutional` collection
- Session memory layer: hot store for current session artifacts
- F2 filter: only returns memories with truth_score ≥ 0.99
- Cross-reference with current `delta_draft` — does memory contradict or confirm?
- Uses `anchor_token` to verify constitutional provenance of retrieved memories
- Returns ranked evidence with constitutional provenance

**Inputs:** `delta_draft`, `session_context`, `anchor_token`, `session_id`, `k` (top-k results)

**Outputs:** `evidence[]`, `memory_delta`, `confirmation_score`, `contradiction_flags[]`

---

### 4. `ASI·SIMULATE`

**Tier:** ASI·Ω
**Trinity:** ASI·Ω
**Constitutional floors:** F5 (Peace² ≥ 1.0), F6 (Empathy κᵣ ≥ 0.70)

**Function:**
World model. Simulate consequences before acting. Forward outcome prediction.
ΔS thermodynamic consequence check. **The agent tests reality in its mind
before touching it.**

**This is the ASI threshold.** AGI reasons and reflects. ASI simulates futures.
The ability to model what has not yet happened is the first mark of meta-intelligence.

**Key behaviours:**

- Simulates 3 outcome branches per proposed action: best / expected / worst case
- ΔS check: does this action increase entropy in the system? If yes, SABAR
- F5 Peace²: non-destructive action check — irreversible actions flagged
- F6 Empathy: identify weakest stakeholder in each simulation branch
- Thermodynamic budget: tracks energy/cost per session, enforces Landauer bound
- Returns `simulation_report` with Landauer bound compliance flag

**Inputs:** `delta_draft`, `evidence[]`, `proposed_actions[]`

**Outputs:** `simulation_report`, `outcome_branches[3]`, `entropy_delta`, `stakeholder_map`

---

### 5. `ASI·CRITIQUE`

**Tier:** ASI·Ω
**Trinity:** ASI·Ω
**Constitutional floors:** F7 (Humility), F8 (Genius G★ ≥ 0.80), F9 (C_dark < 0.30)

**Function:**
Self-evaluation. Metacognition. Calibrated uncertainty. **Knows what it doesn't know.**
F7 Humility gated. The agent's inner critic before it acts.

**This is the ASI self-check.** Before forging a solution, the system interrogates
its own simulation. Is G★ high enough? Is C_dark contained? Is the proposed
solution genuinely good or just clever?

**Key behaviours:**

- F8 Genius: G★ = A×P×X×E² evaluated against simulation_report
- F9 C_dark: detects dark cleverness — solutions technically correct but ethically hollow
- F7 Humility: re-checks uncertainty band — agent must acknowledge limits
- Returns SABAR if critique finds the proposal insufficient
- Emits `critique_verdict`: PASS / REVISE / SABAR

**Inputs:** `simulation_report`, `delta_draft`, `session_context`

**Outputs:** `critique_verdict`, `g_star_score`, `c_dark_score`, `revision_notes[]`

---

### 6. `AGI-ASI·FORGE`

**Tier:** LIMINAL (AGI·Δ + ASI·Ω)
**Trinity:** AGI·Δ∩ASI·Ω
**Constitutional floors:** F11 (Command Auth LOCK), F1 (Amanah — reversible?)

**Function:**
Solution synthesis. Code generation. Creative output. F11-gated execution.
Genius score (G★) evaluated. **Where intelligence becomes action.**

**The naming is the design.** AGI-ASI·FORGE is liminal — it lives at the
threshold between knowing and doing. AGI brings the intelligence; ASI brings
the governance. Neither alone can forge. Both together can.

**Key behaviours:**

- F11 Command Auth: execution requires verified session identity — no anonymous forge
- F1 Amanah: checks reversibility before any write/execute action
- EngineerAgent (Ω-HEART) persona executes under risk-tiered approval
- `action_types`: `synthesize_solution` / `execute_code` / `shell_command` / `write_file` / `read_file`
- `risk_tier` low → auto; medium → warn; high → 888_HOLD required before execution
- G★ post-execution check: was the forged output worthy?

**Inputs:** `critique_verdict`, `simulation_report`, `anchor_token`, `action_type` (caller-supplied), `risk_tier` (caller-supplied)

**Outputs:** `forge_result`, `execution_trace`, `g_star_post`, `reversibility_flag`

> `action_type` and `risk_tier` are **caller-supplied at invocation time** — not derived from
> any upstream tool output. The calling agent or human declares what kind of action to forge
> and at what risk level. The chain does not decide this — sovereign intent does.

---

### 7. `APEX·JUDGE`

**Tier:** APEX·Ψ
**Trinity:** APEX·Ψ
**Constitutional floors:** F3 (Tri-Witness ≥ 0.95), F13 (Sovereign — human final authority)

**Function:**
Sovereign constitutional verdict. Tri-Witness consensus (Human · AI · Earth).
Emits SEAL / VOID / HOLD / PARTIAL / SABAR with governance token.
**The highest intelligence act: judgment.**

**APEX is not the smartest tier — it is the most responsible.** APEX·JUDGE
does not optimize. It decides. And it signs what it decides with cryptographic
authority that the vault will not accept without.

**Key behaviours:**

- Tri-Witness: Human witness (authority score) · AI witness (consistency score) · Earth witness (thermodynamic score)
- Action-class thresholds: read 0.80 / write 0.90 / execute 0.95 / critical 0.98
- Geometric mean: `verdict_confidence = (H × A × E)^(1/3)`
- Mints `governance_token = "{verdict}:{sha256_hmac}"` — timing-safe HMAC
- Uses `anchor_token` to bind verdict cryptographically to the originating session
- F13 Sovereign: human has veto — APEX·JUDGE recommends; human can override to HOLD
- Fail-closed: default `proposed_verdict = VOID` (never SEAL as default)

**Inputs:** `forge_result`, `simulation_report`, `critique_verdict`, `session_context`, `anchor_token`

**Outputs:** `verdict`, `governance_token`, `witness_scores{}`, `verdict_confidence`

---

### 8. `VAULT·SEAL`

**Tier:** VAULT (post-APEX commitment stage)
**Trinity:** APEX·Ψ
**Constitutional floors:** F1 (Amanah — immutable record), F2 (Truth — sealed permanently)

**Function:**
Immutable vault commit. Cryptographic attestation. Hash-chain entry.
**Loop closes → feeds back to INIT·ANCHOR with +trust elevation.**

**The vault is not APEX's tool — it is the vault's.** APEX judges. The vault
commits. These are different authorities. The `governance_token` from APEX·JUDGE
is the only accepted key. No token = no seal. No seal = no loop continuation.

**Key behaviours:**

- Accepts only valid `governance_token` (timing-safe HMAC verify against `anchor_token`)
- Invalid/missing token → VOID, no ledger write (fail-closed)
- Writes hash-chained entry to VAULT999: `{session_id, verdict, evidence_hash, trust_delta, timestamp}`
- Computes `trust_delta` = f(verdict_confidence, G★, witness_scores)
- Returns `vault_receipt` with `next_trust_tier` for INIT·ANCHOR on next loop
- The `sealed_delta` package feeds directly into the next INIT·ANCHOR call

**Inputs:** `governance_token`, `forge_result`, `verdict_confidence`, `session_id`, `anchor_token`

**Outputs:** `vault_receipt`, `ledger_hash`, `trust_delta`, `next_trust_tier`, `sealed_delta`

---

## The Helix — How the Loop Works

```text
Loop N:
  INIT·ANCHOR (trust_tier=T)
    → AGI·REASON  (generates hypotheses + proposed_actions)
    → AGI·REFLECT (mirrors against sealed past)
    → ASI·SIMULATE (tests futures, maps stakeholders)
    → ASI·CRITIQUE (interrogates self, scores G★)
    → AGI-ASI·FORGE (acts, F11-gated)
    → APEX·JUDGE  (decides, mints governance_token)
    → VAULT·SEAL  (commits, returns sealed_delta)
         ↓
Loop N+1:
  INIT·ANCHOR (trust_tier=T+Δ, armed with sealed_delta)
    → AGI·REASON  (richer hypotheses — memory is deeper)
    → AGI·REFLECT (more to reflect — vault is larger)
    → ...
```

**What accumulates across loops:**

| Delta | Carrier | Effect on next loop |
| --- | --- | --- |
| `+trust` | `next_trust_tier` in vault_receipt | INIT·ANCHOR opens at higher authority level |
| `+context` | `sealed_delta` evidence package | AGI·REFLECT finds richer prior evidence |
| `+world model` | Simulation results sealed to vault | ASI·SIMULATE starts from better priors |
| `+governance` | Governance token history in vault | APEX·JUDGE has more Tri-Witness signal |

---

## Tier Summary

```text
INIT    │ INIT·ANCHOR     — Loop entry. Identity. F12 gate. Trust elevation.
AGI·Δ   │ AGI·REASON      — Intelligence. 3-path hypothesis + proposed actions.
        │ AGI·REFLECT     — Memory as mirror. F2-verified reflection.
ASI·Ω   │ ASI·SIMULATE    — World model. Future consequence. Stakeholder map.
        │ ASI·CRITIQUE    — Metacognition. Inner critic. G★ + C_dark check.
LIMINAL │ AGI-ASI·FORGE   — Intelligence meets governance. Action threshold.
APEX·Ψ  │ APEX·JUDGE      — Sovereign judgment. Tri-Witness. Governance token.
VAULT   │ VAULT·SEAL      — Immutable commitment. Loop closes. Trust rises.
```

---

## Naming Rationale

| Old Name | New Name | Why the change matters |
| --- | --- | --- |
| `anchor_session` | `INIT·ANCHOR` | INIT is a stage, not a tier. Anchoring is an initialization act. |
| `AGI·RECALL` | `AGI·REFLECT` | Recall is passive (fetch). Reflect is active (integrate). Memory as mirror. |
| `ASI·FORGE` | `AGI-ASI·FORGE` | Forge lives at the threshold. Neither pure intelligence nor pure governance. |
| `APEX·SEAL` | `VAULT·SEAL` | APEX judges. The vault seals. Different authorities. |

---

## Known Gaps (Intentional)

Per the AGI-to-arifOS mapping established in this session:

- **Web search** — no `AGI·SENSE` equivalent. F2 Truth grounding depends on external tools.
- **Multimodal perception** — no image/audio/doc ingestion tool.
- **Injection defense as standalone** — F12 is embedded in INIT·ANCHOR, not a separate callable.
- **Health monitoring** — no `ASI·VITAL` equivalent. G★ is computed inside ASI·CRITIQUE.
- **Sovereign hold management** — 888_HOLD is embedded in FORGE `risk_tier`, not standalone.

These are intentional omissions. The chain is pure. Extensions belong in
Proposal B (13 tools) or C (21 tools) — the next helix loop of the architecture itself.

---

## Verdict

```text
Tool count:     8
Tier structure: INIT → AGI·Δ → ASI·Ω → LIMINAL → APEX·Ψ → VAULT
Loop type:      Helix (trust-compounding spiral)
Constitutional: F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 F11 F12 F13 — all covered
Spec review:    APPROVED (7 issues found and resolved — v1.1)
Status:         APPROVED BY ARIF — 2026-03-13
Motto:          DITEMPA BUKAN DIBERI
```
