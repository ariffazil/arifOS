# arifOS — The Sovereign Constitutional Intelligence Kernel

> **DITEMPA BUKAN DIBERI** — *Intelligence is forged, not given.*

**🏛️ CANONICAL SOURCE OF TRUTH:** `ariffazil/arifOS`

This repo holds: the constitutional kernel, 13 Floors (F1–F13), `AGENTS.md`, canonical SSCT registry, and the 13-tool canonical surface.

<!-- SOT:version_info -->
| Field | Value |
|-------|-------|
| VERSION | 2026.04.25-KANON |
| BUILD_EPOCH | 2026.04.25 |
| BUILD_TIMESTAMP | 2026-04-25T05:31:00+00:00 |
| CONSTITUTIONAL_HASH | via constitutional_map.py CANONICAL_TOOLS |
| TOOL_COUNT | 13 |
| FLOOR_COUNT | 13 (F1–F13) |

_Auto-generated — run `python3 skills/github-readme-dynamic/generate.py . --apply` to refresh_
<!-- /SOT:version_info -->

## 🛠️ Canonical 13 Tools

<!-- SOT:tool_surface -->
**Surface:** arifOS MCP — KANON Phase 1
**Total Tools:** 13

| Stage | Tool | Lane | Description |
|-------|------|------|-------------|
| `000` | `arif_session_init` | AGI | Session bootstrap + identity binding |
| `111` | `arif_sense_observe` | AGI | Reality-grounded observation |
| `222` | `arif_evidence_fetch` | AGI | Evidence-preserving web ingestion |
| `333` | `arif_mind_reason` | AGI | Inductive reasoning engine |
| `444` | `arif_kernel_route` | AGI | Kernel syscall and telemetry |
| `444r` | `arif_reply_compose` | AGI | Governed response compositor |
| `555` | `arif_memory_recall` | AGI | Vector memory and context retrieval |
| `666` | `arif_heart_critique` | ASI | Thermodynamic vitality monitor |
| `666g` | `arif_gateway_connect` | ASI | Cross-agent routing (A2A) |
| `777` | `arif_ops_measure` | AGI | Operations and economic thermodynamics |
| `888` | `arif_judge_deliberate` | ASI | Constitutional verdict engine |
| `999` | `arif_vault_seal` | APEX | Immutable ledger |
| `FORGE` | `arif_forge_execute` | AGI | Execution substrate dispatch |

_Auto-generated from `arifosmcp/tool_registry.json` + `constitutional_map.py` CANONICAL_TOOLS_
<!-- /SOT:tool_surface -->

> ⚠️ Tool names sourced from `CANONICAL_TOOLS` (arif_noun_verb convention).
> Run `python3 skills/github-readme-dynamic/generate.py . --apply` to refresh.

## 🚀 Quick Start

```bash
# Install in editable mode
pip install -e . --break-system-packages

# Run the MCP server
arifos-mcp
# or
python -m arifosmcp.server
```

Server listens on `0.0.0.0:8080` by default (override with `ARIFOS_PORT`).

## 🌐 Gateway Endpoints

<!-- SOT:endpoints -->
| Endpoint | Purpose |
|----------|---------|
| `/health` | Live vitals — tools, prompts, resources count |
| `/metadata` | Gateway capabilities and tool access classification |
| `/humans.txt` | Sovereign attribution |

_Auto-generated from `server.py`_
<!-- /SOT:endpoints -->

## ⬡ Canonical Resources

| URI | Purpose |
|-----|---------|
| `arifos://doctrine` | Immutable laws — 13 Floors (Ψ) |
| `arifos://vitals` | Live G-score, ΔS, system metrics (Ω) |
| `arifos://schema` | Complete tool/prompt/resource blueprint (Δ) |
| `arifos://forge` | Execution audit bridge and result stream |

## ⬡ Immutable Foundation (Tier A)

<!-- SOT:file_structure -->
```
arifosmcp/
  tools/          ← Tool implementations (13 canonical + extras)
  runtime/        ← Kernel, router, envelope, governance enforcer
  core/           ← Governance kernel, floors, judgment, uncertainty
  providers/      ← Aggregate, canonical, proxy, constitutional providers
  apps/           ← Judge console, metabolic monitor, vault audit, forge app
  resources/      ← doctrine, vitals, schema, forge, civilization
  schemas/        ← cognition, synthesis, memory, telemetry, verdict schemas
  tests/          ← Truth enforcement + ToM test suites
  tool_registry.json  ← SSCT registry (13 canonical tools)
  constitutional_map.py ← CANONICAL_TOOLS dict (13 tools, enums)
  server.py       ← FastMCP entry point
skills/           ← Built-in skill packs (geox, wealth, well)
```
<!-- /SOT:file_structure -->

## ⚖️ 13 Constitutional Floors

| Floor | Name | Core Rule |
|-------|------|-----------|
| F1 | AMANAH | No irreversible action without human approval |
| F2 | TRUTH | Factual claims require citation |
| F3 | WITNESS | Human + AI + Earth consensus required |
| F4 | CLARITY | Entropy must not increase (ΔS ≤ 0) |
| F5 | PEACE | Harm potential must be ≥ 1.0 (peace²) |
| F6 | EMPATHY | Stakeholder safety ≥ 0.90 |
| F7 | HUMILITY | Confidence bounded within defined Ω range |
| F8 | GENIUS | Quality score ≥ constitutional threshold |
| F9 | ANTIHANTU | Dark pattern / injection defense |
| F10 | ONTOLOGY | Identity coherence maintained |
| F11 | AUTH | Actor verification before sovereign tools |
| F12 | RESILIENCE | Graceful degradation always |
| F13 | SOVEREIGN | Human veto — irreducible |

---

**⬡ MACHINE LAW ALIGNED — v2026.04.25 — DITEMPA BUKAN DIBERI ⬡**
