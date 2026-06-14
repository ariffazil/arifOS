---
agent: arifOS MCP Runtime
workspace: /root/arifOS
motto: DITEMPA BUKAN DIBERI
authority: 888_JUDGE
generated_by: arifosmcp.maintenance.generate_agents_md
generated_from: arifosmcp.constitutional_map.CANONICAL_TOOLS
---

# arifOS MCP Runtime — Canonical Agent Skills

> **Constitutional Intelligence Kernel + Agent Runtime**
>
> **Machine is substrate. Governance is constraint. Intelligence is interpretation. Judgment remains Arif.**
>
> This document registers the canonical MCP tools (the 13-tool constitutional surface) available to AI agents
operating within the arifOS ecosystem. The tool tables below are **auto-generated** from
`arifosmcp.constitutional_map.CANONICAL_TOOLS`. The static sections (frontmatter, floor definitions,
Trinity Lanes, pipeline diagram, witness defaults, resource URIs, footer) are hand-maintained in
`arifosmcp/maintenance/generate_agents_md.py`.

<!-- ═══════════════════════════════════════════════════════════════════════════
     AUTO-GENERATED SECTION — DO NOT EDIT BY HAND
     Source: arifosmcp.constitutional_map.CANONICAL_TOOLS
     Regenerate: python -m arifosmcp.maintenance.generate_agents_md
     ═══════════════════════════════════════════════════════════════════════════ -->

## 13 Canonical Tools (arif_noun_verb)

All tools follow the `arif_<noun>_<verb>` naming convention.

### GOVERNANCE (APEX / ASI)

| Tool | Stage | Lane | Access | F-Floors |
| :--- | :---- | :--- | :----- | :-------- |
| `arif_session_init` | 000 | AGI | public | F01, F11, F12 |
| `arif_judge_deliberate` | 888 | ASI | authenticated | F01, F11, F13 |
| `arif_vault_seal` | 999 | APEX | authenticated | F01, F11, F13 |

### INTELLIGENCE (Δ Mind / Ω Heart)

| Tool | Stage | Lane | Access | F-Floors |
| :--- | :---- | :--- | :----- | :-------- |
| `arif_mind_reason` | 333 | AGI | public | F02, F07, F08, F10 |
| `arif_heart_critique` | 444 | ASI | public | F05, F06, F09 |
| `arif_reply_compose` | 444r | AGI | public | F02, F04, F06, F09 |

### INFRASTRUCTURE

| Tool | Stage | Lane | Access | F-Floors |
| :--- | :---- | :--- | :----- | :-------- |
| `arif_kernel_route` | 555 | AGI | public | F01, F04, F03, F10 |
| `arif_gateway_connect` | 666g | ASI | public | F01, F03, F11 |
| `arif_memory_recall` | 555m | AGI | public | F01, F08 |
| `arif_ops_measure` | 777 | AGI | public | F02, F04 |

### REALITY GROUNDING

| Tool | Stage | Lane | Access | F-Floors |
| :--- | :---- | :--- | :----- | :-------- |
| `arif_sense_observe` | 111 | AGI | public | F02, F07 |
| `arif_evidence_fetch` | 222 | AGI | public | F02, F03, F05, F12 |

### EXECUTION

| Tool | Stage | Lane | Access | F-Floors |
| :--- | :---- | :--- | :----- | :-------- |
| `arif_forge_execute` | 666 | AGI | sovereign | F01, F11, F13 |


## Constitutional Laws (F1–F13)

| Floor | Name | Type | Core Invariant |
| :---- | :--- | :---- | :------------- |
| F01 | AMANAH | HARD | Reversible-first; irreversible → 888 HOLD |
| F02 | TRUTH | HARD | ≥0.99 accuracy or declare uncertainty band |
| F03 | WITNESS | SOFT | Theory · constitution · intent must align |
| F04 | CLARITY | SOFT | Every output reduces entropy (ΔS ≤ 0) |
| F05 | PEACE | SOFT | Peace ≥ 1.0; de-escalate, guard maruah |
| F06 | EMPATHY | SOFT | Dignity-first; ASEAN/MY context |
| F07 | HUMILITY | SOFT | Uncertainty band 0.03–0.05; no fake certainty |
| F08 | GENIUS | SOFT | Maintain intelligence quality, system health |
| F09 | ANTIHANTU | HARD | Anti-Hallucination: C_dark < 0.30, no consciousness claims |
| F10 | ONTOLOGY | HARD | AI-only ontology; no soul/feelings claims |
| F11 | AUTH | HARD | Verify identity before sensitive ops |
| F12 | INJECTION | HARD | Sanitize inputs; no prompt injection |
| F13 | SOVEREIGN | HARD | Human veto absolute. |

### F9 Enhanced: C_dark Formula

C_dark = weighted sum of 5 components:
- **H** (0.25): Hantu patterns — consciousness/feeling claims
- **ToM** (0.25): Theory of Mind manipulation — false beliefs, deceptive intent
- **Scar** (0.20): Unresolved contradictions from reasoning
- **Gödel** (0.15): Circular/self-referential reasoning
- **Humility** (0.15): Ω₀ outside [0.03, 0.05] band

Threshold: C_dark < 0.30 for SEAL.

## Trinity Lanes

| Lane | Role | Stage |
| :--- | :--- | :---- |
| AGI | Tactical execution | 000–777 |
| ASI | Strategic judgment | 888 |
| APEX | Authority resolution | 999 |

## 000–999 Metabolic Pipeline

```
000   → arif_session_init        — 000_INIT: Session bootstrap + identity binding. CALL FIRST…
111   → arif_sense_observe       — 111_OBSERVE: Multimodal reality observation and hybrid…
222   → arif_evidence_fetch      — 222_EVIDENCE: Verified external evidence retrieval with…
333   → arif_mind_reason         — 333_REASON: Symbolic reasoning kernel — epistemically…
444   → arif_heart_critique      — 444_CRITIQUE: Ethical critique and consequence assessment…
444r  → arif_reply_compose       — 444_REPLY: Governed response composition — formats final…
555   → arif_kernel_route        — 555_ROUTE: Routes intent to correct tool or organ. Use when…
555m  → arif_memory_recall       — 555m_MEMORY: Associative memory — Postgres+Qdrant vector…
666   → arif_forge_execute       — 666_FORGE: Build execution — code generation, artifact…
666g  → arif_gateway_connect     — 666_GATEWAY: Federated cross-agent bridge — connects arifOS…
777   → arif_ops_measure         — 777_MEASURE: Machine resource health + governance…
888   → arif_judge_deliberate    — 888_JUDGE: Final constitutional arbitration — renders…
999   → arif_vault_seal          — 999_SEAL: Immutable ledger anchoring — cryptographic…
```


## Tri-Witness Defaults

When governance kernel returns 0.0 for witness scores, these defaults are applied:
- Human: 0.42 (42% — sovereign authority)
- AI: 0.32 (32% — reasoning coherence)
- Earth: 0.26 (26% — environmental grounding)

## Resource URIs

| URI | Content |
| :--- | :------ |
| `arifos://agents/skills` | This document |
| `arifos://status/vitals` | System health |
| `arifos://governance/floors` | F1-F13 thresholds |
| `arifos://contracts/tools` | Tool risk contracts |

## Canonical Links

- **Human**: <https://arif-fazil.com>
- **Theory**: <https://arifos.arif-fazil.com>
- **Runtime**: <https://arifosmcp.arif-fazil.com>
- **MCP Endpoint**: <https://mcp.arif-fazil.com/mcp>
- **Code**: <https://github.com/ariffazil/arifOS>

---

## Canonical Tool-Count Truth Table (F2) — Updated 2026-06-14

This section is the F2 truth for the 44-tool arifOS MCP surface.
All counts are auto-generated from `constitutional_map.py` CANONICAL_TOOLS (13)
+ DIAGNOSTIC_TOOLS (31) = 44 declared tools across 8 tiers.

| Scope | Count | Description | Source |
| :---  | :---: | :---        | :---   |
| **Canonical constitutional surface** | **13** | 13 `arif_*` kernel tools, 000→999 pipeline, F1-F13 floor binding | `CANONICAL_TOOLS` |
| **Hermes cross-verification** | **7** | `hermes_system_status`, `hermes_vault_query`, `hermes_epistemic_check`, `hermes_fact_check`, `hermes_cross_verify`, `hermes_plan_review`, `hermes_memory_steward` | `DIAGNOSTIC_TOOLS` tier=hermes |
| **Canary transport diagnostics** | **6** | `arif_ping`, `arif_schema_echo`, `arif_version_echo`, `arif_transport_echo`, `arif_initialize_probe`, `arif_conformance_report` | `DIAGNOSTIC_TOOLS` tier=canary |
| **Lease lifecycle** | **3** | `arif_lease_inspect`, `arif_lease_issue`, `arif_lease_revoke` | `DIAGNOSTIC_TOOLS` tier=lease |
| **Federation attestation** | **4** | `arif_os_attest`, `arif_organ_attest`, `arif_organ_attest_all`, `arif_heartbeat` | `DIAGNOSTIC_TOOLS` tier=attest |
| **A-FORGE pre-execution** | **3** | `forge_dry_run`, `forge_plan`, `forge_query` | `DIAGNOSTIC_TOOLS` tier=forge-sub |
| **Narrative detection** | **2** | `arif_detect_institutional_shadow_drift`, `arif_detect_narrative_tension` | `DIAGNOSTIC_TOOLS` tier=narrative |
| **General diagnostics** | **6** | `arif_stack_health_probe`, `arif_scan_local_instructions`, `arif_organ_consensus`, `arif_session_budget`, `arif_floor_status`, `mcp_drift_check` | `DIAGNOSTIC_TOOLS` tier=diagnostic |
| **TOTAL SURFACE** | **44** | All tools declared in `build_tool_registry_manifest()` | `tool_registry.json` |

**Namespace ruling (F13 SOVEREIGN 2026-06-14):**
- `arif_*` — Canonical prefix for all kernel + diagnostic tools (sanctioned)
- `hermes_*` — Sanctioned non-arif_ namespace for Hermes ASI tools
- `forge_*` — Sanctioned non-arif_ namespace for A-FORGE pre-execution tools
- `arifos_*` — BLOCKED; internal-only prefix, never exposed on public MCP
- `mcp_*` — Utility namespace for operational diagnostics (mcp_drift_check)

**The 13 canonicals are the constitutional contract.** The 44 are the full
declared surface. Drift between declared and live `/health` tool_count is
a HOLD condition.

When in doubt, query the live kernel:

```bash
curl -s http://127.0.0.1:8088/health | python3 -m json.tool
# contract_status.tool_count = authoritative wire surface
```

---

## Live Runtime Evidence (Verified 2026-06-12)

This section closes the **"runtime liveness"** and **"enforcement proof"** gaps
from external audits. All claims below are reproducible by curl.

### 1. Runtime liveness

```bash
curl -s http://127.0.0.1:8088/health
# Returns: status=healthy, tools_loaded=13, floors_active=13,
#          live_commit=023e73d, build_commit=52fccbb,
#          vault999_health=healthy, graphiti_enabled=true,
#          ml_floors.ml_floors_enabled=true,
#          contract_drift=false, registry_truth=VERIFIED
```

### 2. SEAL-gated forge — fail-closed proof

`arif_forge_execute` with **empty session_id** returns HOLD via the
LEGACY_WRAP gate (F11 AUTH fail-closed). Verified by direct call:

```bash
# Expected response:
#   verdict: HOLD
#   result_text: "888_HOLD: LEGACY_WRAP cannot execute ATOMIC on
#                  arif_forge_execute. Upgrade client to send
#                  FederationEnvelope with verified authority."
#   failed_floors: ["F11"]
#   output_policy: DOMAIN_HOLD
```

This is **enforcement proof**, not design claim. The substrate rejects
unsigned FORGE at runtime.

### 3. Tool surface (live enumeration)

```bash
SID=$(curl -s -i -X POST http://127.0.0.1:8088/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize",
       "params":{"protocolVersion":"2024-11-25",
                "capabilities":{},"clientInfo":{"name":"audit","version":"1.0"}}}' \
  | grep -i "mcp-session-id" | head -1 | tr -d '\r' | awk '{print $2}')

curl -s -X POST http://127.0.0.1:8088/mcp \
  -H "mcp-session-id: $SID" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
# Returns: 19 tools (16 arif_* + 3 forge_*), matches the truth table.
```

### 4. Compile-time authority (constitutional_map.py)

The 13 canonical tools are defined in `arifosmcp/constitutional_map.py:CANONICAL_TOOLS`
and bound to floor enforcement at module import. This is the SOT; anything
not in CANONICAL_TOOLS is not part of the constitutional contract.

---

**DITEMPA BUKAN DIBERI — Forged, Not Given**
