---
type: Concept
tags: [architecture, 9+1-tools, metabolic-loop, three-layers, MCP, tools, FAGS-RAPE]
sources: [CHANGELOG.md, ROADMAP.md, K000_LAW.md]
last_sync: 2026-04-08
confidence: 0.95
---

# arifOS Architecture

> **Sources:** `wiki/raw/CHANGELOG.md` (9+1 architecture), `wiki/raw/K000_LAW.md` (floors), `docs/core/ARCHITECTURE.md` (layers)  
> **Current version:** `2026.04.07-SOT-SEALED`

---

## Three-Layer Stack (Air Gap Principle)

arifOS is organized in three nested layers (AAA Architecture), physically and logically separated by the "Air Gap" Principle:

- **AAA (Application Layer)**: A fluid, mutable governance interface where agents interact with the user.
- **CCC (Constitutional Kernel)**: The immutable, rigid metabolic core where the 13 Floors are enforced.
- **BBB (Protocol Bridge)**: The secure, audited data transport between AAA and CCC.

| Layer | Name | What it governs | Key files |
|-------|------|-----------------|-----------|
| 🔴 **Physics** | What IS possible | Thermodynamic constraints, physical limits | `000/FLOORS/K000_LAW.md`, `000/000_MANIFESTO.md` |
| 🟡 **Math** | HOW it is enforced | Algorithmic implementation, floor scoring | `arifosmcp/`, `.agents/`, `core/` (migrated → arifosmcp) |
| 🟢 **Language** | WHO + Context | Identity, memory, user profile, behavior | `docs/core/SOUL.md`, `AGENTS.md`, `wiki/` |

**The recursive stack:**
```
Physics Layer    → Defines what CAN be computed
      ↓
Math Layer       → Defines who MAY authorize
      ↓
Language Layer   → Defines what MATTERS
      ↓
13 Constitutional Floors → Enforces all three at runtime
```

---

## 9+1 Tool Surface (Current Canonical Architecture)

The canonical MCP surface as of `2026.04.06.3-TOM-ANCHORED`:

### 9 Governance Tools (Think / Validate — never execute directly)

| Tool | Role | ToM fields required |
|------|------|-------------------|
| `arifos.init` | Session anchoring | user_intent, assumed_context |
| `arifos.sense` | Reality grounding + evidence gathering | evidence_type, source_confidence |
| `arifos.mind` | Structured multi-hypothesis reasoning | alternative_hypotheses (min 2), second_order_effects |
| `arifos.route` | Lane selection + intent classification | intent_class, priority |
| `arifos.heart` | Safety analysis + human modeling | stakeholder_model, harm_probability |
| `arifos.ops` | Operational cost (irreversibility + rollback) | rollback_plan, estimated_irreversibility |
| `arifos.judge` | Constitutional verdict — **sole SEAL authority** | full_floor_scores, tri_witness |
| `arifos.memory` | Governed context recall | recall_scope, confidence |
| `arifos.vault` | Immutable seal receipt (no execution) | seal_hash, ledger_entry |

### 1 Execution Bridge (Action — gated by SEAL)

| Tool | Role | Gate condition |
|------|------|---------------|
| `arifos.forge` | Delegated execution | `judge verdict = "SEAL"` required |

**Separation of powers:** Think/Validate tools vs. Execute tool. `arifos.forge` cannot run without a prior `arifos.judge` SEAL verdict.

### Tool Modes

Multi-function tools:
- `arifos.judge` → modes: `judge` | `health` | `history` | `validate`
- `arifos.vault` → modes: `seal` | `seal_card` | `render` | `status`

---

## Metabolic Loop (Golden Path)

The canonical execution pipeline every agent session follows:

```
init → sense → mind → heart → judge → vault
  ↓       ↓      ↓       ↓       ↓       ↓
Anchor  Ground  Reason  Safety  Decide  Seal
```

Full 8-stage governed sensing pipeline: `governed_sense_v2`

1. **000_INTAKE** — Ground reality, parse intent
2. **111_SENSE** — Evidence gathering (F10, F11, F12 preprocessing)
3. **222_THINK** — Structured reasoning (F2, F4, F7)
4. **333_ATLAS** — Cross-domain synthesis
5. **444_EVIDENCE** — Empathy-encoded response generation
6. **555_EMPATHY** — Stakeholder impact (F5, F6, F9)
7. **666_ALIGN** — Ethical alignment, Anti-Hantu check (**Floor types (Metabolic Cooling Hierarchy):**
- **HARD** (Breach) — immediate **VOID** verdict. The output is discarded and Recorded as a violation.
- **SOFT** (Instability) — triggers **PARTIAL** or **SABAR** (cooling/refinement) protocol.
- **DERIVED** (Intelligence) — computed from other metric combinations (e.g., Genius G★).

> [!IMPORTANT]
> **Anti-Hantu (F9)** enforces **Ontological Honesty**. The AI is strictly forbidden from claiming a soul, consciousness, or feelings. It must remain a transparent tool.

---

## FAGS RAPE Autonomous Cycle

The autonomy ladder for full-autonomy (FAG) mode:

| Stage | Name | Action |
|-------|------|--------|
| **F**ind (111) | SEARCH | Internal grep or web search first |
| **A**nalyze (333) | ASSESS | Thermodynamic ΔS check |
| **G**overn (444) | ALIGN | 13 LAWS + arifOS checkpoint |
| **S**eal (666) | FORGE | Write code/files (reversible only) |
| **R**eview (777) | VALIDATE | Constitutional validation |
| **A**ttest (888) | FINALIZE | Human+AI+Earth witness |
| **P**reserve (999) | LOG | Cooling Ledger hash-chain |
| **E**vidence (Ledger) | AUDIT | Audit trail |

Every autonomous action must pass `arifos_core.checkpoint()` before execution. Verdict options: SEAL / VOID / PARTIAL / 888_HOLD.

---

## Theory of Mind (ToM) Integration

All 9 governance tools require structured mental-model externalization:

```python
{
  "problem_statement": "...",
  "alternative_hypotheses": ["Path A", "Path B", "Path C"],  # min 2 required
  "second_order_effects": ["Consequence 1", "Consequence 2"],
  "estimated_uncertainty": 0.25,
  "confidence_in_reasoning": 0.85,
}
```

Missing ToM fields → `tom_violation: True` → VOID verdict.

**G★ Scoring** (from ToM input quality):
```
G★ = confidence + adjustments
Factors: confidence estimates, alternative count, assumptions declared,
         second-order effects, consistency checks, harm probability (inverse)
Range: clamped [0, 1]
```

---

## Runtime Stack (as of SOT-SEALED)

```
arifosmcp/          ← Canonical package (all logic here)
├── tools.py        ← 10 canonical tools (ToolSpec, TOOLS)
├── schemas.py      ← Canonical schemas
├── prompts.py      ← Philosophy Registry v1.2.0 (83 quotes)
├── resources.py    ← 8 resources
├── manifest.py     ← arifos.* namespace (no arifos.v2)
├── server.py       ← FastAPI + streamable-http + stdio
├── build_info.py   ← Live git SHA, release_tag
└── sensing_protocol.py ← governed_sense_v2 (8 stages)

Endpoints:
  /health       ← SoT fields: source_repo, floors_active, warnings
  /tools        ← Runtime surface (wins over docs on conflict)
  /.well-known/arifos-index.json ← Canonical index
  /widget/vault-seal ← ChatGPT-compatible UI widget
```

**SoT Rule:** Doctrine conflict → arifOS repo wins. Runtime surface conflict → live `/health` + `/tools` wins.

---

## Philosophy Registry

Civilizational quotes injected at constitutional moments:

| Property | Value |
|----------|-------|
| Version | v1.2.0 |
| Total quotes | 83 (across 5 G★ bands) |
| Selection | Deterministic: `sha256(session_id + band + g_star) % count` |
| Hard override | INIT stage + SEAL verdict → always "DITEMPA, BUKAN DIBERI." |
| Diversity score | 0.85 (target ≥ 0.80) |
| Categories | void, paradox, truth, wisdom, justice, discipline, power, seal |

---

## What Was Eliminated (Historical)

- `core/` directory — 153 files, migrated → `arifosmcp/` (Apr 5, 2026)
- 13 versioned `*_v2.py` files consolidated (Apr 7, 2026)  
- ~6,000 lines of dead/parallel implementations archived (Apr 6.2, 2026)
- `arifos.v2` namespace fully purged
- Docker image: 6.1GB → ~500MB (lean multi-stage build)

---

## Open Questions

- What is the exact `platform=` dispatch mechanism in Path A (how does `_stamp_platform()` route to different output formatters)?
- Is `arifos.mind` the primary locus of ToM fields, or do all 9 governance tools carry the full ToM schema?
- What does the `/dashboard` look like when ΔS + psi_LE gauges ship (H2 roadmap item)?

---

> [!NOTE]  
> This is a CLAIM-confidence 0.95 synthesis. The 9+1 architecture and tool surface are confirmed by `wiki/raw/CHANGELOG.md`. Layer definitions come from `docs/core/ARCHITECTURE.md` (OpenClaw-era) — the layer names are still valid but the file paths reference an older deploy model.

**Related:** [[Concept_Floors]] | [[Changelog]] | [[Roadmap]] | [[What-is-arifOS]]
