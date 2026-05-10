# arifOS Governance Kernel — Roadmap H1–H4

**Version:** v2026.05.10
**Organ:** arifOS (Governance Kernel / 888 JUDGE)
**Maturity:** PRODUCTION (1,106+ commits)
**Seal Authority:** VAULT999
**Status:** SEALED — APEX ratified — **TOOL EMBODIMENT LIVE**

---

## Executive Summary

arifOS is the constitutional governance kernel of the arifOS federation. As of 2026-05-10, the kernel has crossed a critical maturity threshold: **tool embodiment contracts are live**, enforcing lane, compliance tier, plan_id, and judge_verdict requirements for every tool call at both the kernel dispatch layer and the REST HTTP surface. Session continuity is hardened with persistent store fallback and grace-period TTL. The remaining frontier is cryptographic identity attestation (Ed25519/ES256), institutional memory / precedent graphs, and federation treaties.

**arifOS responsibilities by horizon:**

| Horizon | Theme | arifOS Milestones |
|---------|-------|------------------|
| **H1** (Q2–Q3 2026) | Substrate Hardening | VAULT999 provenance, conflict resolver, model registry, **cryptographic attestation** |
| **H2** (Q4 2026–Q1 2027) | Recursive Governance | F14–F18 draft, proof-carrying judgments, **precedent graph** |
| **H3** (Q2–Q3 2027) | AGI-Scale Runtime | TLA+/Coq formal spec, formal verification, **federation treaties** |
| **H4** (Q4 2027+) | Foundational Substrate | RFC-standard kernel, decentralized VAULT999 |

---

## What Changed (2026-05-10)

### ✅ Deployed
- **Tool Embodiment Contracts** (`embodiment_contracts.py`) — 13 canonical tools mapped to lane, tier, plan_id, judge_verdict, reversibility
- **Kernel Embodiment Gate** — `dispatch_with_fail_closed()` enforces embodiment before handler invocation
- **REST Embodiment Gate** — `call_tool_rest()` returns `EMBODIMENT_HOLD` (403) on violation
- **Runtime Attestation** — `GET /runtime/attestation` returns constitution hash, contracts hash, policy state, session stats
- **Session Continuity** — `_ensure_active_record` fallback, 5-min grace period, half-life TTL refresh
- **Session Persistence Fix** — `_arif_session_init` writes enriched session back to `_SESSIONS` before returning
- **Model Registry** — nested provider/family lookup with `rglob` deep-search fallback

### 🔄 Active Frontier
- Cryptographic identity attestation (mock → Ed25519/ES256)
- Institutional memory / precedent graph (audit log → living jurisprudence)
- Federation treaties (discovery → signed delegation contracts)

---

## H1: Substrate Hardening (Q2–Q3 2026)

### H1.0 — Tool Embodiment System (✅ LIVE)

The embodiment contract system is the runtime's immune system. Every tool call is now verified against:

- **Lane** — `allowed_lanes` (AGI, APEX, QUARANTINE)
- **Tier** — `min_tier` (ANONYMOUS → SOVEREIGN)
- **Plan** — `requires_plan_id` for Forge operations
- **Judge** — `requires_judge_verdict` for Forge / Vault / Judge
- **Reversibility** — `reversible` flag for F01 AMANAH gating

**Key behavior:**
- `arif_forge_execute` without `plan_id` + `judge_verdict` → `EMBODIMENT_HOLD`
- `arif_vault_seal` without `judge_verdict` → `EMBODIMENT_HOLD`
- `arif_session_init` correctly creates `lane: AGI`, `tier: SOVEREIGN` for Arif

### H1.1 — Cryptographic Identity Attestation (P0)

Replace the truncated SHA256 mock signature with real sovereign keypair verification.

```yaml
sovereign_identity:
  algorithm: Ed25519  # or ES256
  public_key: "<base64-encoded-pubkey>"  # stored in agent_registry/cards/arif.json
  verification: client-side signing only  # private key NEVER on server
  fallback: F13 SOVEREIGN manual override if crypto infra fails
```

**Target:** Before next session
**Blocked by:** Sovereign key generation workflow (requires Arif decision)

### H1.2 — F14 Recursive Self-Application Floor (DRAFT)

**Status:** Requires APEX decision before ratification
**Dependency:** F13 SOVEREIGN is the fixed-point anchor

> ⚠️ **APEX DECISION REQUIRED:** F14 self-modification proposals must be ratified by human (Arif/APEX) until a meta-Floor exists above F14. Infinite regress risk — F14 cannot judge its own modification proposals without a fixed-point anchor.

**Proposed F14 text (draft):**

```
F14 — RECURSIVE SELF-APPLICATION

1. Scope: Applies when the kernel modifies its own:
   a) Constitutional floors (F1–F14)
   b) Core prompts or system prompts
   c) Topology (organ additions/removals)
   d)权重 (weight) adjustments to governance parameters

2. Constraint: Any F14 self-modification proposal MUST be:
   a) Logged to VAULT999 with full diff
   b) Ratified by F13 SOVEREIGN (human veto) until H2 meta-Floor exists
   c) Accompanied by a reversibility proof (BEND rollback path)

3. Exclusion: Routine tool additions, documentation changes,
   and MCP surface expansions do NOT trigger F14.

4. Boundary: F14 does NOT apply to:
   a) A-FORGE execution parameter tuning
   b) AAA session configuration
   c) Domain organ internal parameters (GEOX, WEALTH, WELL)
```

### H1.3 — 888_JUDGE Latency Budget

Define maximum decision latency per decision class. A-FORGE enforces timeouts.

| Decision Class | Latency Budget | Example |
|----------------|---------------|---------|
| **Reflex** | < 50ms | Session init, health check |
| **Tactical** | < 2s | Tool routing, evidence fetch |
| **Strategic** | < 60s | Constitutional analysis, multi-organ coordination |
| **APEX** | Human-defined | Self-modification proposals, floor changes |

### H1.4 — VAULT999 Receipt Provenance Schema

Cryptographically link every JUDGE receipt to exact tool outputs, parameter hashes, and model versions.

```python
@dataclass
class VaultReceipt:
    receipt_id: str              # UUID v4
    timestamp: datetime          # ISO 8601
    input_hash: str              # SHA-256 of full input
    tool_call_chain: list[ToolCallRecord]
    model_version: str            # e.g., "gpt-5.5-thinking@2026-05-10"
    reasoning_trace: list[ReasoningStep]
    floor_violations: list[FloorViolation]
    verdict: str                 # SEAL / SABAR / VOID
    output_hash: str             # SHA-256 of output
    previous_receipt_hash: str   # Chain to prior receipt
    merkle_root: str            # Merkle root of full receipt
```

### H1.5 — Cross-Organ Conflict Resolver

When GEOX, WEALTH, and WELL emit contradictory evidence, arifOS must have a formal tie-breaking protocol.

**Protocol:**
```
STEP 1 — Detect contradiction (conflict_id, conflicting_agents, type)
STEP 2 — Classify: TYPE_A factual / TYPE_B interpretive / TYPE_C value-based
STEP 3 — Constitutional weighting (arifOS=0.40, GEOX=0.30, WEALTH=0.20, WELL=0.10)
STEP 4 — Resolution: TYPE_A/B → SEAL, TYPE_C → SABAR (human adjudicates)
STEP 5 — VAULT999 record with all three outputs preserved
```

### H1.6 — Model Registry Hardening

arifOS model registry must version-lock all LLM weights and embeddings used in judgment.

```yaml
model:
  id: gpt-5.5-thinking
  version: 2026.05.10
  source: api.openai.com
  fingerprint: SHA-256 of model metadata
  governance_use: [333_MIND, 666_HEART]
  fallback_chain: [gpt-5.5-thinking, qwen-sea-lion-v4, ollama-qwen-7b]
  last_verified: 2026-05-10
  verification_status: ACTIVE
```

---

## H2: Recursive Governance (Q4 2026 – Q1 2027)

### H2.1 — Institutional Memory / Precedent Graph

VAULT999 is an audit log. H2 makes it a **living jurisprudence substrate**.

- **Precedent index** — searchable graph of prior verdicts by tool, domain, risk tier
- **Jurisprudence delta** — detect when new verdicts diverge from precedent (>2σ)
- **Constitutional drift detection** — track floor interpretation evolution across epochs
- **Verdict lineage API** — `GET /vault/verdict-lineage?verdict_id=...`

### H2.2 — Federation Treaty Layer

A2A discovery works; treaties do not. H2 adds signed, time-bounded delegation contracts.

- **Delegation contract schema** — signed, revocable capability grants
- **Inter-agent liability chain** — who is responsible when delegated action fails
- **Treaty verification endpoint** — `POST /gateway/treaty/verify`

### H2.3 — F14–F18 Ratification (Contingent on APEX Decision)

Dependent on H1.2 APEX decision. Target: December 2026.

### H2.4 — Proof-Carrying Judgments

Every arifOS verdict must include a verifiable justification trace.

```
Required proof components:
1. Input commitment: SHA-256 of all input parameters
2. Floor evaluation: Each F1–F13 with pass/fail + reasoning
3. Evidence chain: External data fetched and how it influenced verdict
4. Alternative considered: At least one rejected + reason
5. Confidence interval: Ω_0 score with uncertainty band
6. Reversibility: BEND rollback path (or "not reversible")
```

### H2.5 — Self-Modification Pipeline

```
AAA proposes → arifOS judges (F14) → A-FORGE executes → VAULT999 records
```

ArifOS must be able to reject a self-improvement proposal that increases its own power without commensurate auditability.

---

## H3: AGI-Scale Runtime (Q2–Q3 2027)

### H3.1 — Formal Constitutional Specification

Translate F1–F13 into TLA+ and/or Coq for mechanized proof.

- **TLA+** for liveness/safety properties of the judgment pipeline
- **Coq** for formal verification of floor constraint logic

Target: July 2027.

### H3.2 — Cross-Organ Conflict Resolver (sub-100ms)

Production-grade conflict resolver with <100ms tie-breaking latency.

---

## H4: Foundational Substrate (Q4 2027+)

### H4.1 — arifOS Kernel RFC-Standard

Publish as formal IETF-style RFC with reference implementation.

### H4.2 — Decentralized VAULT999

Blockchain-anchored or CRDT-backed for cross-organizational deployments.

---

## Cross-Cutting Requirements

### Documentation Spine (All Organs)

Every repo must have the 7-file hygiene spine. arifOS owns the templates.

| File | Status in arifOS |
|------|-----------------|
| `README.md` | ✅ Exists |
| `llms.txt` | ❌ Missing |
| `AGENTS.md` | ✅ Exists |
| `STATE.md` | ❌ Missing |
| `TOOLS.md` | ❌ Missing |
| `RUN.md` | ❌ Missing |
| `.env.example` | ❌ Missing |
| `TODO.md` | ✅ Exists (2026-05-10) |
| `ROADMAP.md` | ✅ Exists (2026-05-10) |

**Owner:** arifOS (template authority) — each organ adopts

### MCP Surface Audit

Reconcile tool counts across federation:

| Organ | Claimed | arifOS MCP Registry | Status |
|-------|---------|-------------------|--------|
| arifOS | 13 + 5 meta | ✅ Verified | **EMBODIED** |
| WEALTH | 48 (13×modes) | ⚠️ Needs reconciliation | — |
| WELL | 45 | ⚠️ Needs reconciliation | — |
| GEOX | 15 | ⚠️ Needs reconciliation | — |
| A-FORGE | 20+ | ⚠️ Needs reconciliation | — |

**Action:** Publish unified `MCP_ENDPOINT_REGISTRY` v2.0 with namespace enforcement. Due: June 2026.

### CI/CD Federation Gate

No organ may merge to main if any other organ in the federation has a failing health check.

**Implementation:** Add federation health check to arifOS CI pipeline. Due: July 2026.

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| F14 infinite regress | High | Critical | F13-anchored ratification (APEX decision required) |
| VAULT999 write failure | Low | Critical | 999 FREEZE gate + backup to FileVaultClient |
| Model registry drift | Medium | High | Automated fingerprint verification in CI |
| Cross-organ conflicts unresolved | Medium | High | Sub-100ms resolver (H1.5) |
| Cryptographic identity bypass | Medium | Critical | Client-side signing only, F13 fallback |

---

## APEX Decisions Required Before H2

| Decision | Options | Prerequisite For |
|----------|---------|-----------------|
| F14 bootstrapping | F13-anchored ratification only | F14–F18 ratification |
| Runtime membrane owner | arifOS / A-FORGE / new RUNTIME organ / NONE | H2 architecture |
| WELL cognitive load approach | Engineering sprint (data only) / Research sprint | H2 operator readiness |
| Sovereign keypair workflow | Ed25519 / ES256 / both | H1.1 cryptographic attestation |

---

## Immediate Actions (This Week)

- [ ] **APEX Review:** Arif Fazil ratify H1 scope, approve F14 decision framework, choose keypair algorithm
- [ ] **VAULT999 Schema:** Draft receipt provenance schema (H1.4)
- [ ] **Conflict Resolver:** Draft protocol (H1.5)
- [ ] **Model Registry:** Inventory all models used in federation
- [ ] **MCP Registry:** Begin unified endpoint registry v2.0
- [ ] **Cryptographic Identity:** Design client-side signing workflow for sovereign keypair

---

**DITEMPA BUKAN DIBERI — Governance kernel sovereignty is forged, not given.**

*SEALED: 2026-05-10 | arifOS Governance Kernel — Tool Embodiment LIVE*
