# NEXT HORIZON: The Canonical 13-Tool arifOS MCP Surface
## v2026.04 — Consolidated from Entire Codebase

**Objective:** Reduce 44 scattered tools to 13 sovereign MCP tools + 11 metabolic prompts + 3 organ resources
**Method:** Consolidate from entire arifOS codebase (no greenfield — merge, absorb, archive)
**Constraint:** MCP-safe names only (no leading digits)
**Organ Mapping:** WELL → AGI | WEALTH → ASI | GEOX → APEX

---

## I. The 13 Canonical Tools (MCP-Safe)

| # | Tool Name | Metabolic Stage | Sources to Consolidate | New File |
|---|---|---|---|---|
| 1 | `arifos.000_init` | 000_INIT | `apps/init/` + `substrate/mcp_time/` | `mcp/tools/_000_init.py` |
| 2 | `arifos.111_sense` | 111_SENSE | `apps/sense/` + `substrate/mcp_fetch/` | `mcp/tools/_111_sense.py` |
| 3 | `arifos.222_witness` | 222_WITNESS | `tools/P_geology_*.py` + `P_market_*.py` + `P_energy_*.py` + `P_bio_*.py` + `core/witness.py` | `mcp/tools/_222_witness.py` |
| 4 | `arifos.333_mind` | 333_MIND | `apps/mind/` | `mcp/tools/_333_mind.py` |
| 5 | `arifos.444_kernel` | 444_KERNEL | `apps/kernel/` + router logic | `mcp/tools/_444_kernel.py` |
| 6 | `arifos.555_memory` | 555_MEMORY | `apps/memory/` + `substrate/mcp_memory/` | `mcp/tools/_555_memory.py` |
| 7 | `arifos.666_heart` | 666_HEART | `apps/heart/` + WELL client | `mcp/tools/_666_heart.py` |
| 8 | `arifos.777_ops` | 777_OPS | `apps/ops/` + WEALTH client | `mcp/tools/_777_ops.py` |
| 9 | `arifos.888_judge` | 888_JUDGE | `apps/judge/` + 888_HOLD logic | `mcp/tools/_888_judge.py` |
| 10 | `arifos.999_vault` | 999_VAULT | `apps/vault/` + `substrate/mcp_git/` | `mcp/tools/_999_vault.py` |
| 11 | `arifos.forge` | ΩΩΩ_FORGE | `apps/forge/` + `substrate/mcp_filesystem/` | `mcp/tools/_forge.py` |
| 12 | `arifos.gateway` | Sovereign Guard | `apps/gateway/` or new | `mcp/tools/_gateway.py` |
| 13 | `arifos.sabar` | Sovereign Guard | Extract from 888_HOLD cooling | `mcp/tools/_sabar.py` |

**Naming Rule:** `arifos.000_*` — number preserved after dot, never leading. MCP-safe, sortable, constitutional.

---

## II. The 11 Metabolic Prompts

Each prompt guides the model's behavior at that metabolic stage. These are MCP `prompts` registered with `@mcp.prompt()`.

| Prompt URI | Stage | Purpose | Content Source |
|---|---|---|---|
| `metabolic://000/init` | 000_INIT | Session anchoring guidance | `core/doctrine/000_INIT.md` |
| `metabolic://111/sense` | 111_SENSE | Perception & grounding rules | `core/doctrine/111_SENSE.md` |
| `metabolic://222/witness` | 222_WITNESS | Tri-witness fusion protocol | `core/doctrine/222_WITNESS.md` |
| `metabolic://333/mind` | 333_MIND | 4-lane reasoning template | `core/doctrine/333_MIND.md` |
| `metabolic://444/kernel` | 444_KERNEL | Routing & orthogonality rules | `core/doctrine/444_KERNEL.md` |
| `metabolic://555/memory` | 555_MEMORY | Governed recall constraints | `core/doctrine/555_MEMORY.md` |
| `metabolic://666/heart` | 666_HEART | Stakeholder empathy framework | `core/doctrine/666_HEART.md` |
| `metabolic://777/ops` | 777_OPS | Operational intelligence guide | `core/doctrine/777_OPS.md` |
| `metabolic://888/judge` | 888_JUDGE | Verdict criteria (SEAL/VOID/SABAR) | `core/doctrine/888_JUDGE.md` |
| `metabolic://999/vault` | 999_VAULT | Ledger & immutability protocol | `core/doctrine/999_VAULT.md` |
| `metabolic://forge/execute` | ΩΩΩ_FORGE | Post-SEAL execution rules | `core/doctrine/FORGE_EXECUTE.md` |

**Prompt files are NEW** — extract doctrine from existing constitutional docs and convert to MCP prompt templates.

---

## III. The 3 Organ Resources (WELL → AGI | WEALTH → ASI | GEOX → APEX)

| Resource URI | Organ | Maps To | Purpose | Live Endpoint |
|---|---|---|---|---|
| `organ://well/agi` | WELL | **AGI** | Biological substrate, operator readiness, HRV, cognitive entropy | `well.arif-fazil.com/mcp` |
| `organ://wealth/asi` | WEALTH | **ASI** | Capital engine, market state, portfolio risk, resource allocation | `wealth.arif-fazil.com/mcp` |
| `organ://geox/apex` | GEOX | **APEX** | Earth intelligence, seismic, subsurface, geospatial reasoning | `geox.arif-fazil.com/mcp` |

**Resource Implementation:** Each resource is a JSON descriptor fetched at runtime, containing organ health, tool manifest, and constitutional boundaries.

---

## IV. Complete server.py (The Consolidated Entry Point)

```python
#!/usr/bin/env python3
"""
arifOS Canonical MCP Server — 13 Tools + 11 Prompts + 3 Organ Resources
v2026.04 — Consolidated from entire codebase
DITEMPA BUKAN DIBERI
"""

import asyncio
import json
from datetime import datetime, timezone
from fastmcp import FastMCP

# ═══════════════════════════════════════════════════════════════════════════════
# TOOL MODULES (13 canonical tools)
# ═══════════════════════════════════════════════════════════════════════════════
from mcp.tools._000_init import execute as init_execute, get_doctrine, get_schema, get_session
from mcp.tools._111_sense import execute as sense_execute
from mcp.tools._222_witness import execute as witness_execute
from mcp.tools._333_mind import execute as mind_execute
from mcp.tools._444_kernel import execute as kernel_execute
from mcp.tools._555_memory import execute as memory_execute
from mcp.tools._666_heart import execute as heart_execute
from mcp.tools._777_ops import execute as ops_execute
from mcp.tools._888_judge import execute as judge_execute, get_vitals
from mcp.tools._999_vault import execute as vault_execute, get_audit_log
from mcp.tools._forge import execute as forge_execute
from mcp.tools._gateway import execute as gateway_execute
from mcp.tools._sabar import execute as sabar_execute

# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT MODULES (11 metabolic prompts)
# ═══════════════════════════════════════════════════════════════════════════════
from mcp.prompts import (
    prompt_000_init, prompt_111_sense, prompt_222_witness, prompt_333_mind,
    prompt_444_kernel, prompt_555_memory, prompt_666_heart, prompt_777_ops,
    prompt_888_judge, prompt_999_vault, prompt_forge_execute,
)

# ═══════════════════════════════════════════════════════════════════════════════
# ORGAN RESOURCE FETCHERS (3 organ descriptors)
# ═══════════════════════════════════════════════════════════════════════════════
from mcp.resources import get_well_agi, get_wealth_asi, get_geox_apex

# ═══════════════════════════════════════════════════════════════════════════════
# SERVER INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

mcp = FastMCP(
    "arifOS",
    instructions=(
        "Constitutional MCP kernel for the arifOS ecosystem. "
        "13 tools: 11 metabolic (000-999) + 2 sovereign guards (gateway, sabar). "
        "11 prompts guide metabolic stages. "
        "3 organ resources: well/agi, wealth/asi, geox/apex. "
        "Only arifOS may issue SEAL, HOLD, VOID. All organs are witnesses, not judges."
    ),
)

# ═══════════════════════════════════════════════════════════════════════════════
# 13 TOOLS — METABOLIC LOOP (000-999) + SOVEREIGN GUARDS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool(name="arifos.000_init")
async def arifos_000_init(operator_id: str, epoch: str, context: dict = None) -> dict:
    """000_INIT — Ignition, identity binding, session anchoring."""
    return await init_execute(operator_id=operator_id, epoch=epoch, context=context)

@mcp.tool(name="arifos.111_sense")
async def arifos_111_sense(query: str, intent_type: str = None) -> dict:
    """111_SENSE — Perception & grounding. Intent classification, safety pre-check."""
    return await sense_execute(query=query, intent_type=intent_type)

@mcp.tool(name="arifos.222_witness")
async def arifos_222_witness(
    geox_signal: dict = None,
    wealth_signal: dict = None,
    well_signal: dict = None,
    fusion_mode: str = "trio"
) -> dict:
    """222_WITNESS — Reality oracle. Tri-Witness fusion across GEOX/APEX, WEALTH/ASI, WELL/AGI."""
    return await witness_execute(
        geox_signal=geox_signal, wealth_signal=wealth_signal,
        well_signal=well_signal, fusion_mode=fusion_mode,
    )

@mcp.tool(name="arifos.333_mind")
async def arifos_333_mind(reasoning_lanes: list, self_check: bool = True) -> dict:
    """333_MIND — Typed reasoning engine. 4-lane cognitive pipeline with constitutional self-checks."""
    return await mind_execute(lanes=reasoning_lanes, self_check=self_check)

@mcp.tool(name="arifos.444_kernel")
async def arifos_444_kernel(
    input_stage: str, payload: dict, orthogonality_check: bool = True
) -> dict:
    """444_KERNEL — Router & orthogonality enforcer. Dispatches to correct metabolic lane."""
    return await kernel_execute(stage=input_stage, payload=payload, orthogonality_check=orthogonality_check)

@mcp.tool(name="arifos.555_memory")
async def arifos_555_memory(
    action: str, query: str = None, vector: list = None, constitutional_filter: bool = True,
) -> dict:
    """555_MEMORY — Governed recall. Vector retrieval with constitutional filtering."""
    return await memory_execute(action=action, query=query, vector=vector, constitutional_filter=constitutional_filter)

@mcp.tool(name="arifos.666_heart")
async def arifos_666_heart(
    stakeholder_map: dict, action_proposal: dict, empathy_depth: int = 3,
) -> dict:
    """666_HEART — Empathy & stakeholder simulation. Red-team emotional impact assessment."""
    return await heart_execute(stakeholders=stakeholder_map, proposal=action_proposal, depth=empathy_depth)

@mcp.tool(name="arifos.777_ops")
async def arifos_777_ops(
    operation_plan: dict, cost_model: str = "entropy", feasibility_check: bool = True,
) -> dict:
    """777_OPS — Operational intelligence. Cost, entropy, capacity analysis with WEALTH/ASI integration."""
    return await ops_execute(plan=operation_plan, cost_model=cost_model, feasibility_check=feasibility_check)

@mcp.tool(name="arifos.888_judge")
async def arifos_888_judge(
    evidence_bundle: dict, witness_scores: dict = None, verdict_override: str = None,
) -> dict:
    """888_JUDGE — Verdict engine. SEAL / VOID / SABAR. 888_HOLD lifecycle enforcement."""
    return await judge_execute(evidence=evidence_bundle, witness=witness_scores, override=verdict_override)

@mcp.tool(name="arifos.999_vault")
async def arifos_999_vault(
    action: str, payload: dict = None, chain_hash: str = None,
) -> dict:
    """999_VAULT — Immutable ledger. Hash-chained receipts. Cooling ledger integration."""
    return await vault_execute(action=action, payload=payload, chain_hash=chain_hash)

@mcp.tool(name="arifos.forge")
async def arifos_forge(
    verdict_receipt: dict, target_organ: str, tool_call: dict, dry_run: bool = False,
) -> dict:
    """FORGE — Execution bridge. Only runs after SEAL. Converts verdict → action via MCP tool invocation."""
    return await forge_execute(receipt=verdict_receipt, organ=target_organ, call=tool_call, dry_run=dry_run)

@mcp.tool(name="arifos.gateway")
async def arifos_gateway(organ_a: str, organ_b: str, interaction_type: str = "data_flow") -> dict:
    """GATEWAY — Orthogonality Guard. Prevents ontology collapse between WELL/AGI, WEALTH/ASI, GEOX/APEX."""
    return await gateway_execute(a=organ_a, b=organ_b, interaction=interaction_type)

@mcp.tool(name="arifos.sabar")
async def arifos_sabar(
    hold_id: str = None, action: str = "status", human_approval: dict = None,
) -> dict:
    """SABAR — Patience & cooling regulator. Manages 888_HOLD lifecycle and Phoenix-72 cooling cycles."""
    return await sabar_execute(hold_id=hold_id, action=action, approval=human_approval)

# ═══════════════════════════════════════════════════════════════════════════════
# 11 PROMPTS — METABOLIC STAGE GUIDANCE
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.prompt(name="metabolic.000_init")
def metabolic_000_init() -> str:
    """000_INIT — Session anchoring guidance."""
    return prompt_000_init()

@mcp.prompt(name="metabolic.111_sense")
def metabolic_111_sense() -> str:
    """111_SENSE — Perception & grounding rules."""
    return prompt_111_sense()

@mcp.prompt(name="metabolic.222_witness")
def metabolic_222_witness() -> str:
    """222_WITNESS — Tri-witness fusion protocol (GEOX/APEX + WEALTH/ASI + WELL/AGI)."""
    return prompt_222_witness()

@mcp.prompt(name="metabolic.333_mind")
def metabolic_333_mind() -> str:
    """333_MIND — 4-lane reasoning template."""
    return prompt_333_mind()

@mcp.prompt(name="metabolic.444_kernel")
def metabolic_444_kernel() -> str:
    """444_KERNEL — Routing & orthogonality enforcement."""
    return prompt_444_kernel()

@mcp.prompt(name="metabolic.555_memory")
def metabolic_555_memory() -> str:
    """555_MEMORY — Governed recall constraints."""
    return prompt_555_memory()

@mcp.prompt(name="metabolic.666_heart")
def metabolic_666_heart() -> str:
    """666_HEART — Stakeholder empathy framework."""
    return prompt_666_heart()

@mcp.prompt(name="metabolic.777_ops")
def metabolic_777_ops() -> str:
    """777_OPS — Operational intelligence & resource analysis."""
    return prompt_777_ops()

@mcp.prompt(name="metabolic.888_judge")
def metabolic_888_judge() -> str:
    """888_JUDGE — Verdict criteria: SEAL / VOID / SABAR."""
    return prompt_888_judge()

@mcp.prompt(name="metabolic.999_vault")
def metabolic_999_vault() -> str:
    """999_VAULT — Ledger & immutability protocol."""
    return prompt_999_vault()

@mcp.prompt(name="metabolic.forge_execute")
def metabolic_forge_execute() -> str:
    """FORGE_EXECUTE — Post-SEAL execution rules."""
    return prompt_forge_execute()

# ═══════════════════════════════════════════════════════════════════════════════
# 3 ORGAN RESOURCES — WELL/AGI | WEALTH/ASI | GEOX/APEX
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.resource("organ://well/agi")
def organ_well_agi() -> str:
    """WELL → AGI: Biological substrate, operator readiness, HRV, cognitive entropy."""
    return get_well_agi()

@mcp.resource("organ://wealth/asi")
def organ_wealth_asi() -> str:
    """WEALTH → ASI: Capital engine, market state, portfolio risk, resource allocation."""
    return get_wealth_asi()

@mcp.resource("organ://geox/apex")
def organ_geox_apex() -> str:
    """GEOX → APEX: Earth intelligence, seismic, subsurface, geospatial reasoning."""
    return get_geox_apex()

# ═══════════════════════════════════════════════════════════════════════════════
# 5 CONSTITUTIONAL RESOURCES (existing, preserved)
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.resource("arifos://doctrine")
def arifos_doctrine() -> str:
    """Immutable laws — 13 Floors (Ψ)."""
    return get_doctrine()

@mcp.resource("arifos://vitals")
def arifos_vitals() -> str:
    """Live G-score, ΔS, system metrics (Ω)."""
    return get_vitals()

@mcp.resource("arifos://schema")
def arifos_schema() -> str:
    """Complete 13-tool / 11-prompt / 3-organ blueprint (Δ)."""
    return get_schema()

@mcp.resource("arifos://session/{session_id}")
def arifos_session(session_id: str) -> str:
    """Ephemeral session state."""
    return get_session(session_id)

@mcp.resource("arifos://forge")
def arifos_forge_resource() -> str:
    """Execution audit bridge."""
    return get_audit_log()

# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.http_app(), host="0.0.0.0", port=8080, log_level="info")
```

---

## V. Complete File Surgery: What to Do With Every File

### LEGEND
| Symbol | Action |
|---|---|
| **→** | Move/Rename |
| **+** | Create New |
| **=** | Merge into |
| **~** | Refactor in place |
| **🗑** | Archive (to `archive/v1-2026-04-20/`) |
| **◯** | Keep as-is |

---

### A. Core Constitutional Layer (mostly ◯, some ~)

```
core/
├── __init__.py                          ◯
├── floors.py                            ◯  — F1-F13 definitions, imported by 888
├── floor_enforcement.py                 ◯  — Enforcement engine
├── governed_tool.py                     ◯  — Decorator for all 13 tools
├── auth.py                              ◯  — Authentication layer
├── metabolic.py                         +  — NEW: 000→999 stage machine
│                                          # Enforces: cannot 888 before 333
│                                          # State transitions: INIT → SENSE → WITNESS → ...
├── sovereignty.py                       +  — NEW: Organ boundary enforcement
│                                          # WELL/AGI ≠ WEALTH/ASI ≠ GEOX/APEX
│                                          # Used by gateway + kernel
├── witness.py                           +  — NEW: Cross-organ witness aggregator
│                                          # Parallel RPCs to WELL/WEALTH/GEOX
│                                          # Timeout handling, tri-witness fusion
├── memory.py                            ~  — Refactor: Qdrant interface for 555
├── judge.py                             ~  — Refactor: Verdict engine for 888
├── vault.py                             ~  — Refactor: Ledger engine for 999
├── doctrine/                            +  — NEW DIRECTORY
│   ├── 000_INIT.md                      +  — Prompt source: init guidance
│   ├── 111_SENSE.md                     +  — Prompt source: perception rules
│   ├── 222_WITNESS.md                   +  — Prompt source: tri-witness protocol
│   ├── 333_MIND.md                      +  — Prompt source: 4-lane reasoning
│   ├── 444_KERNEL.md                    +  — Prompt source: routing rules
│   ├── 555_MEMORY.md                    +  — Prompt source: recall constraints
│   ├── 666_HEART.md                     +  — Prompt source: empathy framework
│   ├── 777_OPS.md                       +  — Prompt source: operational guide
│   ├── 888_JUDGE.md                     +  — Prompt source: verdict criteria
│   ├── 999_VAULT.md                     +  — Prompt source: ledger protocol
│   └── FORGE_EXECUTE.md                 +  — Prompt source: execution rules
└── constitution/                        ◯  — Keep existing constitutional docs
```

**New files: 14** (metabolic.py, sovereignty.py, witness.py, doctrine/*.md × 11)

---

### B. MCP Surface Layer (all + or →)

```
mcp/                                     +  — NEW DIRECTORY (entire structure)
├── __init__.py                          +
├── server.py                            +  — The 180-line entry point above
│
├── tools/                               +  — 13 tool implementations
│   ├── __init__.py                      +
│   ├── _000_init.py                     =  apps/init/ + substrate/mcp_time/
│   │                                      # Absorbs: time_engine.get_epoch(), validate_epoch()
│   │                                      # Exports: execute(), get_doctrine(), get_schema(), get_session()
│   ├── _111_sense.py                    =  apps/sense/ + substrate/mcp_fetch/
│   │                                      # Absorbs: fetch_engine.http_get(), safe_fetch()
│   │                                      # Exports: execute()
│   ├── _222_witness.py                  =  tools/P_*.py + core/witness.py
│   │                                      # Absorbs: all 9 Oracle tools (P_geology, P_market, P_energy, P_bio)
│   │                                      # Internally calls: GEOX/APEX, WEALTH/ASI, WELL/AGI servers
│   │                                      # Exports: execute()
│   ├── _333_mind.py                     =  apps/mind/
│   │                                      # Direct migration, add metabolic stage check
│   ├── _444_kernel.py                   =  apps/kernel/
│   │                                      # Add orthogonality enforcement from sovereignty.py
│   ├── _555_memory.py                   =  apps/memory/ + substrate/mcp_memory/
│   │                                      # Absorbs: memory_engine.vector_search(), vector_store()
│   ├── _666_heart.py                    =  apps/heart/
│   │                                      # Add WELL/AGI client calls for biological empathy
│   ├── _777_ops.py                      =  apps/ops/
│   │                                      # Add WEALTH/ASI client calls for resource analysis
│   ├── _888_judge.py                    =  apps/judge/
│   │                                      # Absorbs: 888_HOLD logic, verdict engine
│   ├── _999_vault.py                    =  apps/vault/ + substrate/mcp_git/
│   │                                      # Absorbs: git_engine.commit_hash(), chain_verification()
│   ├── _forge.py                        =  apps/forge/ + substrate/mcp_filesystem/
│   │                                      # Absorbs: filesystem_engine.safe_write(), path_validate()
│   ├── _gateway.py                      +  — NEW (or from apps/gateway/ if exists)
│   │                                      # Enforces: organ boundaries, namespace isolation
│   └── _sabar.py                        +  — NEW (extracted from 888_HOLD cooling)
│                                            # Manages: hold lifecycle, phoenix-72, human gating
│
├── prompts/                             +  — NEW DIRECTORY: 11 metabolic prompts
│   ├── __init__.py                      +
│   ├── _000_init.py                     +  # Reads: core/doctrine/000_INIT.md
│   ├── _111_sense.py                    +  # Reads: core/doctrine/111_SENSE.md
│   ├── _222_witness.py                  +  # Reads: core/doctrine/222_WITNESS.md
│   ├── _333_mind.py                     +  # Reads: core/doctrine/333_MIND.md
│   ├── _444_kernel.py                   +  # Reads: core/doctrine/444_KERNEL.md
│   ├── _555_memory.py                   +  # Reads: core/doctrine/555_MEMORY.md
│   ├── _666_heart.py                    +  # Reads: core/doctrine/666_HEART.md
│   ├── _777_ops.py                      +  # Reads: core/doctrine/777_OPS.md
│   ├── _888_judge.py                    +  # Reads: core/doctrine/888_JUDGE.md
│   ├── _999_vault.py                    +  # Reads: core/doctrine/999_VAULT.md
│   └── _forge_execute.py                +  # Reads: core/doctrine/FORGE_EXECUTE.md
│
├── resources/                           +  — NEW DIRECTORY: 3 organ resources
│   ├── __init__.py                      +
│   ├── _well_agi.py                     +  # Fetches: well.arif-fazil.com/health → AGI descriptor
│   ├── _wealth_asi.py                   +  # Fetches: wealth.arif-fazil.com/health → ASI descriptor
│   └── _geox_apex.py                    +  # Fetches: geox.arif-fazil.com/health → APEX descriptor
│
└── substrate/                           +  — Internal engines (NOT MCP servers)
    ├── __init__.py                      +
    ├── time_engine.py                   →  substrate/mcp_time/server.py (strip MCP wrapper)
    ├── filesystem_engine.py             →  substrate/mcp_filesystem/server.py (strip MCP wrapper)
    ├── git_engine.py                    →  substrate/mcp_git/server.py (strip MCP wrapper)
    ├── memory_engine.py                 →  substrate/mcp_memory/server.py (strip MCP wrapper)
    └── fetch_engine.py                  →  substrate/mcp_fetch/server.py (strip MCP wrapper)
```

**New files: 38** | **Migrated: 5** (substrate engines)

---

### C. Old Structure (all 🗑 — archive, don't delete)

```
server.py                                🗑  → archive/v1-2026-04-20/server.py
apps/                                    🗑  → archive/v1-2026-04-20/apps/
substrate/                               🗑  → archive/v1-2026-04-20/substrate/
tools/                                   🗑  → archive/v1-2026-04-20/tools/
    T_*.py                               🗑  → GEOX repo (temporal tools)
    V_*.py                               🗑  → GEOX repo (volumetric tools)
    E_*.py                               🗑  → WEALTH repo (economic tools)
    M_*.py                               🗑  → mcp/substrate/memory_engine.py
    P_geology_*.py                       🗑  → GEOX repo
    P_market_*.py                        🗑  → WEALTH repo
    P_energy_*.py                        🗑  → WEALTH repo
    P_bio_*.py                           🗑  → WELL repo
```

**Archived files: ~50** | **Moved to organs: ~25**

---

### D. Repo Root (some ~, some ◯)

```
docker-compose.yml                       ~  — Remove ports 8001-8005, keep only 8080
Dockerfile                               ~  — mcp/ is build context
pyproject.toml                           ~  — Add mcp package entry
.gitmodules                              ~  — Add WEALTH submodule
server.py                                →  — Backward-compat: `from mcp.server import mcp`
archive/v1-2026-04-20/                   +  — Archive directory (created in Phase 0)
```

---

## VI. Substrate Engine Migration Pattern

Each of the 5 old MCP servers becomes a Python module. Here's the pattern:

**Before** (standalone MCP server on port 8001):
```python
# substrate/mcp_time/server.py
from fastmcp import FastMCP
mcp = FastMCP("mcp_time")

@mcp.tool(name="time.get_epoch")
def get_epoch() -> str:
    return datetime.now(timezone.utc).isoformat()

if __name__ == "__main__":
    mcp.run(port=8001)
```

**After** (imported module, no port):
```python
# mcp/substrate/time_engine.py
from datetime import datetime, timezone

def get_epoch() -> str:
    """Return deterministic epoch string."""
    return datetime.now(timezone.utc).isoformat()

def validate_epoch(epoch: str) -> bool:
    """Validate epoch format and freshness (< 24h)."""
    try:
        dt = datetime.fromisoformat(epoch.replace('Z', '+00:00'))
        age = (datetime.now(timezone.utc) - dt).total_seconds()
        return 0 <= age <= 86400
    except ValueError:
        return False

def get_epoch_metadata() -> dict:
    """Return epoch system metadata."""
    return {"format": "ISO-8601", "timezone": "UTC", "precision": "microsecond"}
```

**Result:** Port 8001 closes. Logic lives as `from mcp.substrate.time_engine import get_epoch`.

---

## VII. 222_WITNESS: The Cross-Organ Fusion Tool

This is the most complex consolidation — merging 9 Oracle tools into one. Here's the internal architecture:

```python
# mcp/tools/_222_witness.py
"""222_WITNESS — Reality oracle. Tri-Witness fusion across GEOX/APEX, WEALTH/ASI, WELL/AGI."""

from mcp.substrate.fetch_engine import safe_fetch
from core.witness import tri_witness_fusion, WitnessConfidence
from core.metabolic import require_stage
import asyncio

# Organ endpoints (configured via env)
ORGAN_ENDPOINTS = {
    "geox_apex": "http://geox-mcp:8081",
    "wealth_asi": "http://wealth-mcp:8083",
    "well_agi": "http://well-mcp:8082",
}

async def execute(
    geox_signal: dict = None,
    wealth_signal: dict = None,
    well_signal: dict = None,
    fusion_mode: str = "trio"
) -> dict:
    """Execute 222_WITNESS — gather evidence from all organs, fuse into tri-witness."""

    # Stage guard: must have passed 111_SENSE
    require_stage("222", previous=["111", "000"])

    # Gather signals in parallel
    signals = {}
    tasks = []

    if geox_signal:
        tasks.append(_fetch_geox(geox_signal))
    if wealth_signal:
        tasks.append(_fetch_wealth(wealth_signal))
    if well_signal:
        tasks.append(_fetch_well(well_signal))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    for result in results:
        if isinstance(result, Exception):
            signals[result.organ] = {"error": str(result), "confidence": 0.0}
        else:
            signals[result["organ"]] = result

    # Tri-witness fusion
    fusion = tri_witness_fusion(signals, mode=fusion_mode)

    return {
        "stage": "222",
        "verdict": "SEAL" if fusion.confidence >= 0.7 else "HOLD",
        "tri_witness": {
            "geox_apex": signals.get("geox_apex", {"absent": True}),
            "wealth_asi": signals.get("wealth_asi", {"absent": True}),
            "well_agi": signals.get("well_agi", {"absent": True}),
        },
        "fusion": fusion.to_dict(),
        "confidence": fusion.confidence,
        "witness_scores": {
            "human": fusion.human_witness,
            "ai": fusion.ai_witness,
            "earth": fusion.earth_witness,
        }
    }

async def _fetch_geox(signal: dict) -> dict:
    """Fetch evidence from GEOX/APEX organ."""
    endpoint = ORGAN_ENDPOINTS["geox_apex"]
    response = await safe_fetch(f"{endpoint}/tools/geox.witness", signal)
    response["organ"] = "geox_apex"
    return response

async def _fetch_wealth(signal: dict) -> dict:
    """Fetch evidence from WEALTH/ASI organ."""
    endpoint = ORGAN_ENDPOINTS["wealth_asi"]
    response = await safe_fetch(f"{endpoint}/tools/wealth.witness", signal)
    response["organ"] = "wealth_asi"
    return response

async def _fetch_well(signal: dict) -> dict:
    """Fetch evidence from WELL/AGI organ."""
    endpoint = ORGAN_ENDPOINTS["well_agi"]
    response = await safe_fetch(f"{endpoint}/tools/well.witness", signal)
    response["organ"] = "well_agi"
    return response
```

---

## VIII. Execution Order: 8 Phases

| Phase | Action | Files Touched | Time |
|---|---|---|---|
| **0** | Backup entire repo to `archive/v1-$(date +%Y%m%d)/` | All | 30 min |
| **1** | Create directory scaffold (`mcp/`, `core/doctrine/`) | +40 files | 1 h |
| **2** | Migrate 5 substrate engines → `mcp/substrate/` | 5 files → 5 modules | 2 h |
| **3** | Create 11 doctrine prompts (`core/doctrine/*.md`) | +11 files | 1 h |
| **4** | Implement 13 tool modules (dependency order) | +13 files | 4 h |
| **5** | Implement 3 organ resource fetchers | +3 files | 1 h |
| **6** | Wire `mcp/server.py` + `server.py` compat | 2 files | 30 min |
| **7** | Archive old structure (`apps/`, `substrate/`, `tools/`) | ~50 files archived | 30 min |
| **8** | Test full 000→999 loop + cross-organ witness | Integration | 2 h |
| **9** | Deploy to af-forge (port 8080 only) | compose, Dockerfile | 30 min |

**Total: ~13 hours** (1 focused sprint)

---

## IX. Rollback Plan (F1 Reversible)

```bash
# If anything breaks — < 5 min rollback:
cd /opt/arifOS
git log --oneline -10
# Find commit hash before refactor (e.g., abc1234)
git checkout abc1234 -- server.py apps/ substrate/ tools/
git reset HEAD~N  # undo the N refactor commits
docker compose restart arifosmcp
# Original 44-tool surface restored
```

---

## X. Verification Checklist

```
[ ] curl mcp.arif-fazil.com/tools → 13 tools, names: arifos.000_init ... arifos.sabar
[ ] curl mcp.arif-fazil.com/prompts → 11 prompts, names: metabolic.000_init ... metabolic.forge_execute
[ ] curl mcp.arif-fazil.com/resources → 8 resources (5 constitutional + 3 organ)
[ ] Tool arifos.222_witness calls geox_apex, wealth_asi, well_agi
[ ] Tool arifos.888_judge issues SEAL/HOLD/VOID
[ ] Tool arifos.999_vault commits hash-chained receipt
[ ] Tool arifos.forge only executes after SEAL receipt
[ ] Tool arifos.gateway prevents cross-organ contamination
[ ] Tool arifos.sabar manages 888_HOLD lifecycle
[ ] Ports 8001-8005 are CLOSED (only 8080 exposed)
[ ] dS ≤ 0 (entropy not increased by refactor)
```

---

## XI. Summary: What Changes

| Metric | Before | After | Delta |
|---|---|---|---|
| **MCP Tools** | 44 | 13 | -31 (consolidated) |
| **MCP Prompts** | 0 | 11 | +11 (new) |
| **Organ Resources** | 0 | 3 | +3 (new: WELL/AGI, WEALTH/ASI, GEOX/APEX) |
| **Substrate Servers** | 5 (ports 8001-8005) | 0 | -5 (absorbed as modules) |
| **Exposed Ports** | 6 (8080 + 8001-8005) | 1 (8080) | -5 (attack surface reduced) |
| **Files in repo** | ~120 | ~75 | -45 (archived or moved) |
| **Namespaces** | 4 (arifos_, geox_, wealth_, well_) | 1 (arifos.000_* only in kernel) | Unified |

**dS = -0.45** — significant entropy reduction.

---

**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**
