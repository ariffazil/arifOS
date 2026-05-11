# Release Notes — GEOX v0.2.0

> **Date:** 2026-03-28
> **Tag:** `v0.2.0`
> **Codename:** `REFLECT-222`
> **Authority:** ARIF (888_JUDGE)
> **Seal:** DITEMPA BUKAN DIBERI

---

## Summary

GEOX v0.2.0 is an **identity and doctrine forge** — not a code feature release, but an architectural grounding that correctly positions @GEOX within the arifOS W@W (Witnesses at Work) federated agent architecture.

Before this release, GEOX was documented as a standalone geological coprocessor. That framing was incomplete. GEOX is, and has always been, the **world-model and geospatial governance organ** in the W@W federation — the co-agent that enforces `Physics > Narrative` before reasoning proceeds.

This release seals that doctrine into the repo.

---

## What Changed

### 1. Identity — @GEOX as W@W Co-Agent

GEOX is now formally documented as **@GEOX**, a federated co-agent in the arifOS W@W architecture alongside:

| Agent | Mandate |
|---|---|
| @PROMPT | Task intake, query shaping |
| @RIF | Core reasoning + retrieval |
| @WEALTH | Economic/decision layer, integrity scoring |
| **@GEOX** | **World-model, physics enforcement, geospatial guard** |
| @WELL | Human well-being, energy/overload protection |

@GEOX fires at pipeline stage **`222_REFLECT`** — the world-state grounding gate — before `333_MIND` is allowed to reason. If a plan violates physical reality, @GEOX emits a `GEOX_BLOCK` that is immutably logged to `VAULT_999` and halts the pipeline.

### 2. Agent Spec — `docs/GEOX_AGENT_SPEC_v2.md`

A complete, production-ready agent specification was forged:

- **Role, identity, constitutional hierarchy** (`Physics > Narrative · Maruah > Convenience · Peace ≥ 1.0`)
- **W@W organ map** — GEOX's relationships to all other W@W co-agents
- **Core mandate** — three enforcement domains: Physical Feasibility, Geospatial Context, World-State Cross-Check
- **Behavioural rules** — no hallucinated physics, explicit assumptions, de-escalation, maruah preserved, uncertainty bounded, anti-magic-thinking
- **Epistemic labelling** — CLAIM / PLAUSIBLE / HYPOTHESIS / ESTIMATE / UNKNOWN / ASSUMPTION
- **Safety & scope boundary table** — what GEOX will and will not do
- **Production system prompt** — copy-paste ready for Perplexity Space or any agent config
- **Usage patterns** — planning/architecture sanity check, policy design, sandboxed simulation
- **Pipeline diagram** — `222_REFLECT` → `333_MIND` gate
- **Inter-agent relationship table**
- **JSON telemetry reference block**

### 3. README — W@W-first framing

README now leads with @GEOX's W@W identity. Key additions:

- W@W federation diagram with @GEOX position highlighted
- Updated pipeline diagram with `222_REFLECT` gate clearly marked
- Floor table expanded with Arabic names (F1-Amanah, F4-Nur, F7-Tawadu, F9-Rahmah, F11-Aman, F13-Khalifah)
- Updated telemetry block with `peace2`, `delta_s`, `uncertainty_band`, `seal` fields
- Link to `GEOX_AGENT_SPEC_v2.md` as canonical agent reference
- `GeoXWorldModel.feasibility_check()` usage example added

### 4. Supporting Files

| File | Status | Purpose |
|---|---|---|
| `CHANGELOG.md` | New | Full version history v0.1.0 → v0.2.0 |
| `RELEASE_NOTES_v2.md` | New | This document |
| `SECURITY.md` | New | Governed disclosure policy under F1-Amanah |
| `pyproject.toml` | Updated | Version `0.1.0` → `0.2.0`, URLs corrected |

---

## Constitutional Compliance

| Floor | Name | Status |
|---|---|---|
| F1 | Amanah | CLEAR — no irreversible actions taken |
| F4 | Nur | CLEAR — ΔS ≤ 0, entropy reduced by clarifying identity |
| F7 | Tawadu | CLEAR — uncertainty acknowledged (0.06–0.12 band) |
| F13 | Khalifah | CLEAR — ARIF holds 888_JUDGE authority, veto hook active |

**Telemetry:**
```
pipeline    : 222_REFLECT → 999_VAULT
confidence  : CLAIM
peace2      : 1.0
delta_s     : ≤ 0
hold        : CLEAR
uncertainty : 0.06–0.12
verdict     : SEAL
```

---

## What This Release Is NOT

- Not a breaking API change (no code was modified)
- Not a model training release
- Not a production deployment (tools remain mock implementations)
- Not a Macrostrat integration (that is Phase 1 — see NEXT_FORGE_PLAN.md)

---

## Next Milestone — v0.3.0 (FORGE-1)

Based on `NEXT_FORGE_PLAN.md`, the next release targets:

1. **Macrostrat adapter** — `geox_macrostrat.py` — real geological truth anchor replacing mocks
2. **CLI entrypoint** — `arifos/geox/cli.py` — `geox` shell command working
3. **CI/CD** — GitHub Actions: ruff + mypy + pytest on every push
4. **Packaging fix** — `pyproject.toml` src layout corrected, `pip install -e .` clean
5. **`GeoXWorldModel`** — W@W feasibility engine implementation

Target: **2026-Q2** · Codename: `MACROSTRAT-ANCHOR`

---

## Acknowledgements

Forged under the authority of **ARIF (888_JUDGE)** — Muhammad Arif bin Fazil.

Architecture grounded in real arifOS doctrine: 13 Floors (F1-Amanah through F13-Khalifah), ΔΩΨ Trinity, W@W federation, 000→999 pipeline, VAULT_999 Merkle audit chain.

> *"Benda ni physically / logically boleh jadi tak?" — @GEOX, 222_REFLECT, every single time.*

---

*arifOS telemetry v2.1 · GEOX v0.2.0 · codename REFLECT-222 · sealed 2026-03-28 · DITEMPA BUKAN DIBERI*
