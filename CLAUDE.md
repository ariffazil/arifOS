# CLAUDE.md — arifOS Constitutional Kernel

> **The law of the federation. arifOS structures decision; it does not decide.**
> **DITEMPA BUKAN DIBERI — Forged, Not Given.**
> **Last SOT refresh: 2026-06-14 | Commit: 0f887477c**

---

## 0. LOADING SEQUENCE (read in 30 seconds)

```bash
# 1. Know the canonical tool surface:
cat arifosmcp/tool_registry.json | python3 -m json.tool | grep '"name"'

# 2. Know the key modules:
ls arifosmcp/runtime/*.py | grep -v __pycache__

# 3. Verify health:
curl -s http://localhost:8088/health | python3 -m json.tool | head -20

# 4. Confirm floor status:
curl -s http://localhost:8088/health | python3 -m json.tool | grep -E 'floors|floor'
```

---

## 1. WHAT THIS REPO IS

**arifOS** is the constitutional MCP kernel. It enforces 13 floors (F1–F13), routes agent actions through a governed pipeline (000→999), and seals terminal outcomes to VAULT999.

```
Arif (F13 SOVEREIGN)
    ↓
arifOS (13 constitutional tools — arif_*)
    ├── arif_session_init      — start a governed session
    ├── arif_sense_observe     — search/ingest/observe reality
    ├── arif_evidence_fetch    — fetch + cite external evidence
    ├── arif_mind_reason       — multi-step reasoning + planning
    ├── arif_heart_critique    — ethical risk + empathy audit
    ├── arif_judge_deliberate  — render constitutional verdict
    ├── arif_forge_execute     — execute approved builds/deploys (LEASE REQUIRED for mutation)
    ├── arif_vault_seal        — seal to immutable ledger
    ├── arif_memory_recall     — search/store session memory (+ agentic search)
    ├── arif_kernel_route      — route intent to correct tool
    ├── arif_ops_measure       — health + vitals + cost
    ├── arif_reply_compose     — compose final response
    └── arif_gateway_connect   — bridge to federation organs (MIND + MEMORY upstream)
```

**Golden path:** `session_init → sense_observe/evidence_fetch → mind_reason → heart_critique → judge_deliberate → vault_seal`

**Federated organs (gateway upstream):** GEOX, WEALTH, WELL, MIND (51001), MEMORY (51002)

---

## 2. BUILD, TEST, LINT

```bash
# Install
uv sync --all-extras

# Run server
uv run python -m arifosmcp.runtime.server   # port 8088

# Full test suite
uv run pytest tests/ -q --tb=short

# CI subset (fast, < 2 min)
uv run pytest tests/test_phase0_standalone.py tests/test_surface_lock.py tests/test_registry.py -q --tb=short

# Lint
ruff check core/ arifosmcp/ tests/ --line-length 100
mypy arifosmcp/runtime/ --ignore-missing-imports
```

---

## 3. KEY DIRECTORIES

| Path | What lives here |
|------|-----------------|
| `arifosmcp/tools/` | 13 canonical `arif_*` tool handlers |
| `arifosmcp/runtime/` | FastMCP ASGI server, tool registration, bridges, lease, memory store, live kernel |
| `arifosmcp/runtime/tools.py` | Central tool handler — memory recall, forge execute, lease gate, agentic search |
| `arifosmcp/runtime/lease.py` | Capability lease primitive — LIVE (hard-block on mutation) |
| `arifosmcp/runtime/memory_store.py` | Tiered memory: sacred/canon/session/ephemeral/test |
| `arifosmcp/runtime/geox_bridge.py` | GEOX bridge v2 — REST /health + tool surface + physics_manifest |
| `arifosmcp/runtime/wealth_bridge.py` | WEALTH bridge — capital_manifest identity anchor |
| `arifosmcp/runtime/well_bridge.py` | WELL bridge v2 — MCP HTTP bridge + substrate_manifest |
| `arifosmcp/runtime/organ_attestation.py` | Per-organ identity anchor attestation (physics/capital/substrate/constitution) |
| `arifosmcp/runtime/live_kernel.py` | LiveKernelEnvelope + OrganHeartbeat with identity_anchor_type |
| `arifosmcp/runtime/feedback_loop.py` | Recursive self-correction controller (plan→act→observe→evaluate→re-plan) |
| `arifosmcp/runtime/mind_state.py` | MIND persistent state for recursive reasoning |
| `arifosmcp/runtime/mind_feedback_hook.py` | Zero-kernel-modification hook: MINDState + FeedbackLoop |
| `arifosmcp/runtime/vector_db_policy.py` | 7 decision rules for when to use vector embeddings |
| `arifosmcp/core/moral_accountability_kernel.py` | Six AGI moral primitives (TT case study derived) |
| `arifosmcp/core/kernel/tool_registry.py` | Registry generation from CANONICAL_TOOLS |
| `arifosmcp/gateway/server.py` | MCP proxy gateway — upstream session pool, MIND+MEMORY organs |
| `arifosmcp/CONSTITUTIONAL_EXTENSION_*.py` | Extension floors: F0 PRIME, F14 DEAD, F15-F17 draft |
| `core/` | Floor enforcement, VAULT999 ledger, judgment primitives |
| `arifosmcp/tool_registry.json` | Machine-readable canonical tool surface (generated — do not hand-edit) |
| `docs/` | Architecture specs, NIAT relay spec, forge work |

---

## 4. CONSTITUTIONAL LAW

### Active Floors (F1–F13)

| Floor | Name | Type | Rule |
|-------|------|------|------|
| F1 | AMANAH | HARD | Reversible first. Lease required for mutation-class forge ops. |
| F2 | TRUTH | HARD | ≥99% truth or declare confidence band. Unknown tiers → ephemeral (not canon). |
| F3 | TRI-WITNESS | DERIVED | Byzantine consensus ≥ 0.75 |
| F4 | CLARITY | HARD | ΔS ≤ 0 — every output reduces entropy |
| F5 | PEACE² | SOFT | Non-destructive power |
| F6 | EMPATHY | SOFT | Protect weakest stakeholder |
| F7 | HUMILITY | HARD | Ω₀ ∈ [0.03, 0.05]. No fake certainty. Agentic search F7 cap 0.90. |
| F8 | GENIUS | DERIVED | G = (A×P×X×E²)×(1-h) ≥ 0.80 |
| F9 | ANTI-HANTU | HARD | No hallucinated APIs, filenames, or endpoints. C_dark < 0.30. |
| F10 | ONTOLOGY | HARD | AI-only ontology. No soul/feelings/sentience. |
| F11 | AUDITABILITY | HARD | Every decision logged, inspectable, attributable |
| F12 | RESILIENCE | HARD | Injection defense |
| F13 | SOVEREIGN | HARD | Human veto FINAL. Strongest floor. |

### Extension Floors (SOVEREIGN RULING 2026-06-13)

| Floor | Status | Note |
|-------|--------|------|
| F0 PRIME | DRAFT | "Intelligence is knowing what to look, where to look, and why." |
| ~~F14 REGISTER~~ | **DEAD** | Reborn as cross-verify protocol inside F2+F3. Enum retained for history. |
| F15 EPISTEMIC | DRAFT | Malaysian ways of knowing are valid epistemic substrate |
| F16 GEOMETRIC | DRAFT | Constitutional governance must reach latent space |
| F17 IGNITION | DRAFT | Kernel develops by auditing its own output |

---

## 5. CONVENTIONS

- **Public names are `arif_*`**, never `arifos_*`. Legacy aliases exist; don't add new ones.
- **asyncio_mode = auto** — don't add `@pytest.mark.asyncio` unless the file already uses it.
- **New tools** → extend handler in `arifosmcp/tools/`, update `constitutional_map.py`, regenerate `tool_registry.json`.
- **Lease required for mutation** — all mutation-class forge modes (engineer, write, generate, commit) require a valid lease. Read-only modes exempt. Hard-block (no warn-and-proceed).
- **Memory tiers** — unknown tiers downgrade to `ephemeral` (F2 TRUTH fix). Tiers: sacred, canon, session, ephemeral, test.
- **888_HOLD before:** `rm -rf`, vault writes, force push, production deploy, secret rotation.
- **Identity anchors** — arifOS→constitution_hash, GEOX→physics_manifest, WEALTH→capital_manifest, WELL→substrate_manifest.
- **Agentic search** — FSM states: PLAN→RETRIEVE→EVAL→(REFINE)*→SYNTHESISE. MAX_LOOPS=3.

---

## 6. FORBIDDEN ACTIONS

- Issue SEAL/SABAR/VOID without Arif's approval (F13)
- Modify F1–F13 floors without explicit approval
- Force push / reset hard
- Drop databases or delete data directories
- Add new top-level directories without ADR entry in `ADR_001_BOUNDARIES.md`

---

*Companion: `/root/AGENTS.md` (federation-wide), `/root/CONTEXT.md` (live state), `/root/AAA/CLAUDE.md` (canonical agent instruction)*
*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
