# arifOS MCP Tool Surface — Red Team Audit
**Date:** 2026-05-19  
**Auditor:** Constitutional Clerk (L3 AGI)  
**Doctrine:** DITEMPA BUKAN DIBERI  
**Trigger:** [Tomaz Bratanic, TDS May 2026] — "One Flexible Tool Beats a Hundred Dedicated Ones"

---

## Audit Question

> Are the 13 canonical tools expressive enough that the agent *composes*, or have we accidentally built the same narrow-tool trap with extra steps?

---

## 1. Quantitative Baseline

| Metric | arifOS | Typical MCP Server (Neo4j/GitHub) | Verdict |
|--------|--------|-----------------------------------|---------|
| **Public tools** | 13 | 4–20 per service | ✅ Disciplined |
| **Total modes** | 104 | N/A (usually 1 mode ≈ 1 tool) | ⚠️ High |
| **Avg modes / tool** | 8.0 | ~1 | ❌ Menu-sprawl risk |
| **Avg params / tool** | 6.5 | 3–8 | ✅ Manageable |
| **Schema token cost** | ~1,005 tokens | ~2,000–5,000+ per server | ✅ Lean |
| **Irreversible tools** | 2 (vault, forge) | Varies | ✅ Controlled |
| **Internal composition chains** | 2 (reply→heart, judge→vault) | Rare | ⚠️ Sparse |
| **Runtime lines behind wrappers** | ~10,781 | Varies | ❌ Opacity risk |

**Key quantitative insight:** The 13-tool count is architecturally sound, but **104 modes is the hidden menu**. An agent using arifOS still picks from ~100 discrete operations. The difference between "200 narrow tools" and "13 tools with 104 modes" is smaller than the surface suggests.

---

## 2. Qualitative Analysis — Tool-by-Tool

### Tier A: Genuinely Expressive Primitives (Agent Composes)

| Tool | Primitive | Mode Depth | Composition |
|------|-----------|------------|-------------|
| `arif_sense_observe` | **Perception** | Deep — search/ingest/compass use different backends (Brave, DDGS, geospatial) | Agent chains sense → evidence |
| `arif_evidence_fetch` | **Evidence** | Deep — fetch/search/verify/void_audit are lifecycle stages; `thinking_depth` parameterizes cognitive effort | Agent chains evidence → reason |
| `arif_mind_reason` | **Cognition** | Deep — plan/reflect/verify/critique/axioms are distinct cognitive postures (branched in `runtime/mind_reason.py`) | Agent chains reason → critique |
| `arif_heart_critique` | **Ethics** | **Deepest** — 7 modes each map to distinct prompt templates and output shapes (`critique` → risks; `simulate` → outcomes; `redteam` → attacks) | Agent chains critique → judge |
| `arif_kernel_route` | **Routing** | Deep — `bridge` dispatches to GEOX/WEALTH; `441_surprise` triggers self-repair; `intent` routes by cognitive axis | Agent uses route to bridge organs |
| `arif_judge_deliberate` | **Judgment** | Deep — `judge` mode is a genuine primitive (SEAL/HOLD/VOID/SABAR); others are utility stubs | Agent chains judge → seal |
| `arif_vault_seal` | **Immutability** | Deep — seal/verify/chain/list/dry_run are different operations on one ledger abstraction | Agent uses seal to anchor |

**Verdict for Tier A:** These 7 tools are the *expressive core*. They offer genuine primitives with semantic depth. The agent composes them into the canonical pipeline (`init → sense → evidence → reason → critique → judge → seal`).

---

### Tier B: Pre-Baked Workflows (Agent Picks, Does Not Compose)

| Tool | Problem | Evidence |
|------|---------|----------|
| `arif_reply_compose` | **Mandatory heart gate** — every call triggers `arif_heart_critique(mode="critique")` before formatting. The agent cannot say "compose without critiquing." The workflow is baked in. | `reply.py` line ~180: pre-delivery gate |
| `arif_forge_execute` | **Auto-governance triad** — auto-detects side effects, auto-checks WELL clarity, auto-registers cooldown. The agent passes a mode and manifest; the tool decides the governance workflow. | `forge.py`: side-effect detection + WELL gate + cooldown registration |
| `arif_judge_deliberate` | **Auto-preload trap** — hardcodes WELL substrate + vitals + governance preload before deliberation. Auto-seals to vault if `vault_entry_id` provided. Three hardcoded steps the agent cannot decompose. | `judge.py`: pre-loads ops + well; post-SEAL vault hook |

**Verdict for Tier B:** These tools *describe* primitives but *implement* workflows. The agent is not composing — it is triggering a pre-baked pipeline. This is the narrow-tool trap wearing primitive clothing.

---

### Tier C: Menu-of-Reports / CRUD Trap

| Tool | Problem | Evidence |
|------|---------|----------|
| `arif_ops_measure` | **16 mode branches**, but `genius`, `psi_le`, `omega`, `landauer`, `constitutional_health`, `metabolic-pulse` return hardcoded JSON stubs. The tool is a telemetry *menu*, not a measurement primitive. | `runtime/tools.py`: `if mode == "genius": return {"g_score": 0.97, ...}` |
| `arif_memory_recall` | **12 modes**, but `store`/`recall`/`search`/`prune`/`context`/`stats`/`audit` are textbook CRUD. `asset_query`/`asset_store` duplicate the same pattern. | `memory.py`: classic CRUD surface |
| `arif_gateway_connect` | **9 modes**, but `discover` returns a hardcoded list of 8 agents; `handshake` returns `uuid.uuid4().hex[:16]`. Mostly stubs. | `gateway.py`: canned JSON responses |
| `arif_session_init` | `discover`/`status` are utility modes on a lifecycle primitive. `cleanup`/`handover` are thin wrappers. | `session.py`: lifecycle + utilities |

**Verdict for Tier C:** These are the clearest narrow-tool trap violations. The agent picks from a menu of pre-canned operations rather than composing a primitive.

---

## 3. The Mode-Sprawl Taxonomy

Of the **104 declared modes**, how many are *genuine semantic branches* vs *stubs/aliases/utilities*?

| Category | Count | % | Examples |
|----------|-------|---|----------|
| **Genuine cognitive branches** | ~35 | 34% | heart:critique/simulate/redteam; mind:plan/reflect/verify; sense:search/ingest/compass |
| **Lifecycle variants** | ~20 | 19% | init:init/resume/validate; vault:seal/verify/list/chain |
| **Utility stubs** | ~30 | 29% | ops:genius/psi_le/omega; gateway:discover/handshake; memory:stats/audit/context |
| **CRUD operations** | ~19 | 18% | memory:store/recall/search/prune; evidence:void_audit |

**Red-team verdict:** Only **~34% of modes are genuinely expressive**. The remaining **66%** are lifecycle variants, utility stubs, or CRUD — exactly the "pile of dedicated tools" pattern the article warns against, just folded into `mode` parameters.

---

## 4. Composition Topology

### What Exists (Sparse)
```
arif_reply_compose ──► arif_heart_critique     [mandatory pre-delivery gate]
arif_judge_deliberate ──► arif_vault_seal      [post-SEAL auto-hook, conditional]
```

### What Is Missing (The Gap)
- **No first-class pipeline DAG.** The canonical sequence (`init → sense → evidence → reason → critique → judge → seal`) is documented everywhere but not enforced or executable.
- **No pipe operator.** Unlike CLI `|`, MCP tools cannot stream intermediate results without round-tripping through the agent's context.
- **No `--params-from-stdin` equivalent.** The agent must format outputs into inputs manually, paying token cost for intermediates.
- **No fan-out / fan-in.** The kernel can `bridge` to other organs, but the agent cannot say "run sense on 3 queries in parallel, then reason over the combined evidence."

**Comparison with CLI ideal:**
```bash
# CLI: model writes once, data flows through bash
gh issue list ... | jq -c '.[]' | while read issue; do neo4j-cli ...; done

# arifOS MCP: model must be the pipe
sense_result = sense_observe(query="...")          # round-trip 1
evidence_result = evidence_fetch(url=...)            # round-trip 2
reason_result = mind_reason(query=evidence_result)   # round-trip 3
# ... every intermediate rides the conversation
```

**Verdict:** arifOS is *not* a CLI replacement. It is a *governance layer* for CLI-like composition. The agent still pays the MCP round-trip tax. The constitutional floors (F1-F13) are the justification for this tax — but the tax is real.

---

## 5. Blast Radius vs. Expressiveness

| Tool | Expressiveness Score | Blast Radius | Governance Load |
|------|---------------------|--------------|-----------------|
| `arif_heart_critique` | ★★★★★ | Low | Self-contained |
| `arif_mind_reason` | ★★★★☆ | Low | Self-contained |
| `arif_sense_observe` | ★★★★☆ | Medium | F11 injection guard |
| `arif_evidence_fetch` | ★★★★☆ | Medium | F-WEB evidence gate |
| `arif_kernel_route` | ★★★★☆ | Medium | Bridge auth |
| `arif_judge_deliberate` | ★★★☆☆ | **High** | WELL preload + auto-vault |
| `arif_forge_execute` | ★★☆☆☆ | **Critical** | Side-effect auto-detect + cooldown |
| `arif_vault_seal` | ★★★★☆ | **Critical** | F1 ack + judge packet |
| `arif_ops_measure` | ★☆☆☆☆ | Low | None (stubs) |
| `arif_memory_recall` | ★★☆☆☆ | Low | Sacred-tier gate |
| `arif_gateway_connect` | ★☆☆☆☆ | Low | None (stubs) |
| `arif_reply_compose` | ★★☆☆☆ | Medium | Mandatory heart gate |
| `arif_session_init` | ★★★☆☆ | Low | F11 auth |

**Insight:** The two most blast-radius-critical tools (`forge_execute`, `vault_seal`) are also the most workflow-pre-baked. The governance layer is load-bearing, but it is *embedded inside the tool* rather than *composable by the agent*. This is exactly the trade-off the article describes.

---

## 6. Honest Verdict: Did We Build the Trap?

### No — Architecturally
- **13 tools** is disciplined. The naming convention (`noun_verb` = cognitive primitive) is correct.
- No per-environment duplication (one arifOS kernel, not 3 per database).
- The canonical pipeline (`sense → evidence → reason → critique → judge → seal`) is a *composition grammar*, not a menu.

### Yes — Implementationally
- **104 modes** is menu-sprawl in disguise.
- **~66% of modes** are stubs, CRUD, or utility variants.
- **Tier B tools** (reply, forge, judge) bake workflows that the agent cannot decompose.
- **No first-class composition operators** (pipe, fan-out, params-from-stdin).

### The Real Shape
arifOS is not "200 narrow tools." It is:

> **7 expressive primitives + 3 pre-baked workflows + 3 CRUD menus**

Folded into 13 names. The *names* are right. The *mode depth* is uneven. The *composition infrastructure* is missing.

---

## 7. Recommendations (Ranked by Impact)

### R1: Merge Stub Modes (High Impact, Low Risk)
- `arif_ops_measure`: Replace 11 modes with 2 — `measure(metric="...")` and `health`.
- `arif_gateway_connect`: Replace 9 modes with 2 — `connect(action="...")` and `discover`.
- Target: reduce 104 → ~60 modes.

### R2: Expose Composition Primitives (High Impact, Medium Risk)
- Add `arif_kernel_route(mode="pipeline", tasks=[...])` — accepts a DAG of tool calls, executes them server-side, returns only final outputs.
- Add `params_from_context` — allows tool N to read tool N-1's output from a session-scoped key, not from the agent's context.

### R3: Decompose Tier B Workflows (Medium Impact, High Risk)
- `arif_reply_compose`: Make the heart gate **optional** (default on, but agent can set `skip_heart_gate=True` with elevated ack).
- `arif_judge_deliberate`: Split WELL preload into a separate `arif_ops_measure(mode="well_preload")` call. Let the agent compose it, not assume it.
- `arif_forge_execute`: Replace modes with a single `execute(manifest_type="...", manifest="...")` where the manifest describes the operation and its governance requirements.

### R4: Document the Composition Grammar (Low Impact, Low Risk)
- Add a `COMPOSITION.md` that teaches agents how to chain the 7 Tier A primitives.
- Include token-cost estimates for each pipeline stage.

### R5: Reduce Runtime Opacity (Medium Impact, Low Risk)
- Split `runtime/tools.py` (10,781 lines) into `runtime/tools/*.py` — one file per tool. The agent reads `--help` or `SKILL.md` more easily when behavior is not buried in a monolith.

---

## 8. Bottom Line

> **The 13-tool surface avoids the narrow-tool trap. The 104-mode implementation does not.**

The article's thesis is validated by arifOS's architecture and violated by its implementation depth. The constitutional governance layer (888_JUDGE, VAULT999, F1-F13) is load-bearing — but it is currently *inside* the tools rather than *around* them.

The ideal arifOS MCP surface:
- **Fewer modes** (target: 30–40, not 104)
- **More manifest-driven parameters** (agent describes intent, tool interprets)
- **First-class composition** (pipeline mode, context streaming)
- **Governance as wrapper, not filler** (floors check the composition, not replace it)

**DITEMPA BUKAN DIBERI.** The shape is right. The forging continues.

---

*Audit sealed. No irreversible actions recommended at this time.*
