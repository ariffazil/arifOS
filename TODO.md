# TODO — arifOS Constitutional Kernel

> **Last Updated:** 2026-05-10
> **Session:** Governance Attestation + Tool Embodiment Deployment
> **Seal:** DITEMPA BUKAN DIBERI

---

## ✅ Completed This Session

- [x] **Tool Embodiment Contracts** — 13 canonical tools mapped to lane/tier/plan/judge requirements
- [x] **Embodiment Enforcement** — Kernel + REST surface both gate execution before handler invocation
- [x] **Runtime Attestation Endpoint** — `GET /runtime/attestation` returns constitution hash, contracts hash, policy state
- [x] **Session Continuity Fix** — `session_auth.py` falls back to persisted store, adds grace period + TTL refresh
- [x] **Session Persistence Fix** — `_arif_session_init` writes enriched session (agent_card, model_governance_card) back to `_FileSessionStore`
- [x] **Model Registry Fix** — `gpt-5.5-thinking` spec added + `registry.py` deep-search fallback for nested provider dirs
- [x] **Container Recreation** — `arifosmcp` recreated to pick up `ARIFOS_REGISTRY_ROOT` + model registry volume mount
- [x] **Pre-push Hook Fix** — Hook now checks `OLD_REMOTE_SHA..LOCAL_SHA` instead of all git history

---

## 🔴 P0 — Critical (Before Next Session)

### Cryptographic Identity Attestation
The current `actor_signature` uses a truncated SHA256 mock hash. The runtime *recognizes* Arif but cannot *cryptographically verify* Arif.

- [ ] **Store sovereign public key** in `agent_registry/cards/arif.json` under `public_key` field
- [ ] **Replace mock signature verification** in `_arif_session_init` with Ed25519 or ES256 verification
- [ ] **Private key hygiene** — sovereign private key must NEVER touch the server; signing happens client-side
- [ ] **Update `signature_verified`** field to reflect real cryptographic truth, not placeholder

**Blocked by:** Sovereign key generation + client-side signing workflow design (requires Arif decision).

### C4 Security Debt — Unrotated Secrets
- [ ] **WEALTH Supabase key** in git history — rotate + purge from history (requires `git filter-repo` or BFG)
- [ ] **arif-sites OpenCode/Telegram tokens** — rotate + remove from tracked files
- [ ] **8 unrotated secrets on disk** — audit with `detect-secrets` + `truffleHog`

**Blocked by:** Sovereign dashboard access + explicit approval for history rewrite (F01 AMANAH).

---

## 🟠 P1 — High (Next 7 Days)

### Institutional Memory / Precedent Graph
VAULT999 is an audit log, not a *living jurisprudence substrate*.

- [ ] **Precedent index** — searchable graph of prior verdicts by tool, domain, risk tier
- [ ] **Jurisprudence delta** — detect when new verdicts diverge from precedent (>2σ threshold)
- [ ] **Constitutional drift** — track how floor interpretation evolves across epochs
- [ ] **Verdict lineage API** — `GET /vault/verdict-lineage?verdict_id=...` returns full ancestry

### Federation Treaty Layer
A2A discovery works; treaties do not.

- [ ] **Delegation contract schema** — signed, time-bounded, revocable capability grants
- [ ] **Inter-agent constitutional liability chain** — who is responsible when delegated action fails
- [ ] **Treaty verification endpoint** — `POST /gateway/treaty/verify` checks delegation chain validity

### Embodiment Contract Refinement
What we built today is v1. Needs dynamic constraints:

- [ ] **WELL readiness coupling** — adjust allowed risk tier based on operator cognitive load
- [ ] **Temporal constraints** — e.g., "Forge allowed only 08:00–22:00 MYT"
- [ ] **Contextual constraints** — e.g., "Vault seal requires WELL clarity > 0.7"
- [ ] **Embodiment contract versioning** — contracts must evolve without breaking legacy sessions

---

## 🟡 P2 — Medium (Next 30 Days)

### Formal Specification
- [ ] **Latency budgets per decision class** — Reflex <50ms, Tactical <2s, Strategic <60s, APEX human-defined
- [ ] **Add latency metadata** to `arif_judge_deliberate` output schema
- [ ] **A-FORGE kill signal integration** — enforce timeout budgets with process termination

### Cross-Organ Conflict Resolver
- [ ] **Detect contradiction** — when GEOX, WEALTH, WELL emit contradictory evidence
- [ ] **Classify contradiction type** — Factual (TYPE_A), Interpretive (TYPE_B), Value-based (TYPE_C)
- [ ] **Constitutional weighting** — default weights: arifOS=0.40, GEOX=0.30, WEALTH=0.20, WELL=0.10
- [ ] **Sub-100ms resolver** — production-grade tie-breaking for H3 scale

### Model Registry Hardening
- [ ] **Version-lock all LLM weights** — fingerprint every model used in judgment
- [ ] **Fallback chain specification** — e.g., `qwen-sea-lion-v4 → llama-sea-lion-v35 → ollama-qwen-7b`
- [ ] **Automated fingerprint verification** in CI — fail build if model hash mismatches

---

## 🟢 P3 — Backlog (H2 2026)

### F14 — Recursive Self-Application Floor
- [ ] Draft F14 text for APEX review
- [ ] Self-modification pipeline: AAA proposes → arifOS judges → A-FORGE executes → VAULT999 records
- [ ] Reversibility proof (BEND rollback path) for every self-modification

### Formal Verification
- [ ] **TLA+ spec** for liveness/safety of judgment pipeline
- [ ] **Coq proofs** for floor constraint logic
- [ ] Target: July 2027

### Decentralized VAULT999
- [ ] Blockchain-anchored or CRDT-backed for cross-organizational deployments
- [ ] H4 2027+

---

## Principles
- **F01 AMANAH** — No history rewrite without explicit sovereign ack
- **F09 ANTI-HANTU** — No consciousness claims in any roadmap text
- **F13 SOVEREIGN** — Arif's veto is absolute on F14+ and irreversible ops
- **DITEMPA BUKAN DIBERI** — Intelligence is forged, not given
