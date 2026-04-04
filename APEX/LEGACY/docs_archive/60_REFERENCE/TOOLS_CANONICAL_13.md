# Canonical 13-Tool Surface (Baseline @ 62cffa2)

Source basis: `aaa_mcp/server.py`, `arifos_aaa_mcp/server.py`, `arifos_aaa_mcp/contracts.py`, `aaa_mcp/protocol/schemas.py`, `aaa_mcp/protocol/tool_naming.py`.

## Canonical Tool Table

| Tool Name | Status | AAA Stage | Input (minimum) | Output (minimum) | Example Call |
|---|---|---|---|---|---|
| `anchor_session` | active | `000_INIT` | `query` | `verdict, stage, session_id` | `{"name":"anchor_session","arguments":{"query":"start","actor_id":"ops"}}` |
| `reason_mind` | active | `111-444` (collapsed) | `query, session_id` | `verdict, stage, session_id` | `{"name":"reason_mind","arguments":{"query":"analyze","session_id":"S1"}}` |
| `vector_memory` | active | `555_RECALL` | `query, session_id` | `verdict, stage, session_id` | `{"name":"vector_memory","arguments":{"query":"x","session_id":"S1"}}` |
| `simulate_heart` | active | `555-666` (merged) | `query, session_id` | `verdict, stage, session_id` | `{"name":"simulate_heart","arguments":{"query":"impact","session_id":"S1"}}` |
| `critique_thought` | active (native in `arifos_aaa_mcp`) | `666_ALIGN` | `plan, session_id` | `verdict, stage, session_id` | `{"name":"critique_thought","arguments":{"plan":{"step":"a"},"session_id":"S1"}}` |
| `apex_judge` | active (needs stage relabel) | `888_APEX_JUDGE` (target canon) | `session_id, query` | `verdict, stage, session_id` | `{"name":"apex_judge","arguments":{"session_id":"S1","query":"decide"}}` |
| `eureka_forge` | active (hold-gated, needs stage relabel) | `777_EUREKA_FORGE` (target canon) | `action_payload, session_id, signature` | `verdict, stage, session_id` | `{"name":"eureka_forge","arguments":{"action_payload":{},"session_id":"S1","signature":"sig"}}` |
| `seal_vault` | active | `999_VAULT` | `session_id, summary` | `verdict, stage, session_id` | `{"name":"seal_vault","arguments":{"session_id":"S1","summary":"done"}}` |
| `search_reality` | active | utility (Delta) | `query` | `status, results` | `{"name":"search_reality","arguments":{"query":"MCP spec"}}` |
| `fetch_content` | active | utility (Delta) | `id` | `status, content|error` | `{"name":"fetch_content","arguments":{"id":"https://example.com"}}` |
| `inspect_file` | active | utility (Delta) | `path` | `status/payload envelope` | `{"name":"inspect_file","arguments":{"path":"."}}` |
| `audit_rules` | active | utility (Delta) | `audit_scope` (optional) | `verdict, scope, details` | `{"name":"audit_rules","arguments":{"audit_scope":"quick"}}` |
| `check_vital` | active | utility (Omega) | none | `status/health payload` | `{"name":"check_vital","arguments":{}}` |

## AGENTS 11 vs Runtime 13 Reconciliation

777/888 canonical directive (Arif):
- `777` = EUREKA FORGE
- `888` = APEX Judge Metabolic Layer

Baseline divergence:
- runtime currently presents `eureka_forge` as `888_FORGE`
- runtime currently presents `apex_judge` as `777-888`

AGENTS-listed verbs (11):
- `anchor, reason, integrate, respond, validate, align, forge, audit, seal, search, fetch`

Runtime canonical public tools (13):
- `anchor_session, reason_mind, recall_memory, simulate_heart, critique_thought, apex_judge, eureka_forge, seal_vault, search_reality, fetch_content, inspect_file, audit_rules, check_vital`

Observed mapping drift:
- many legacy verbs are now aliases or folded flows (`integrate/respond` folded into `reason_mind`; `forge/audit` folded into `apex_judge` path)
- utility surface expanded beyond AGENTS 11-list

Missing-2 request tracking (from AGENTS baseline):
- `[RESEARCH NEEDED]` canonical governance ratification for the two extra utility endpoints beyond AGENTS list: `inspect_file`, `check_vital`
- `[RESEARCH NEEDED]` confirm whether AGENTS should be upgraded to explicit 13-tool canonical names (current text remains legacy-verb oriented)

## Alias and Deprecation Hints (baseline only)

From `aaa_mcp/protocol/tool_naming.py`:
- canonical -> legacy examples:
  - `anchor_session -> init_gate`
  - `reason_mind -> agi_reason`
  - `simulate_heart -> asi_empathize`
  - `apex_judge -> apex_verdict`
  - `seal_vault -> vault_seal`
- legacy 9-verb aliases still resolved:
  - `anchor/reason/integrate/respond/validate/align/forge/audit/seal`

Note: full deprecation lineage is deferred to Phase 2 per your instruction.

## Omega0 and Confidence

- Ω0 estimate (tool census): `0.05`
- Confidence: `0.93`
