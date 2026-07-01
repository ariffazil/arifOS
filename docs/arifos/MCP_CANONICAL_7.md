# arifOS MCP Canonical 7 — Public Surface Reference

> **Scope:** public wire surface exposed by `arifOS` MCP server.  
> **Gated surface:** diagnostic/operator tools (`arif_canary`, `arif_os_attest`, `arif_retrieve_tools`, etc.) are hidden unless `ARIFOS_MCP_EXPOSE_DEV_TOOLS=true`.  
> **Golden path:** `init` → `observe` → `think` → `route` → `judge` → `act` → `seal`

| # | Tool | Stage | Authority | When to call |
|---|------|-------|-----------|--------------|
| 1 | `arif_init` | 000 INIT | advisory | No session yet; start here. Binds actor identity. |
| 2 | `arif_observe` | 111 PROBE | advisory | Evidence gap — search, fetch, vitals, repo map. |
| 3 | `arif_think` | 333 MIND | advisory | Reasoning gap — plan, critique, verify, metabolize. |
| 4 | `arif_route` | 555 ROUTE | advisory | Tool uncertainty — route intent to correct organ. |
| 5 | `arif_judge` | 888 JUDGE | sovereign-gated | Decision time — constitutional verdict (SEAL/HOLD/SABAR/VOID). |
| 6 | `arif_act` | 900 ACT | sealed-only | Execute an approved action; requires prior SEAL. |
| 7 | `arif_seal` | 999 VAULT | sovereign-gated | Finality — append to immutable VAULT999 ledger. |

---

## 1. arif_init — Bootstrap

**Purpose:** Create a governed constitutional session and bind actor identity.

**Modes:** `init` (default) | `light` | `resume` | `validate` | `epoch_open` | `epoch_seal` | `opt_out` | `opt_out_profiling`

**Key params:**
- `mode` — default `init`
- `actor_id` — optional sovereign/agent identity
- `session_id` — for resume/validate
- `ack_irreversible` — required for `opt_out`

**Returns:** `session_id`, authority level, surface pointers, initial invariants, verdict geometry.

**Next step:** `arif_observe` or `arif_triage`.

---

## 2. arif_observe — Ground

**Purpose:** Ground the session in current reality via multimodal sensing.

**Modes:** `search` (default) | `hybrid_discovery` | `ingest` | `compass` | `atlas` | `entropy_dS` | `vitals`

**Key params:**
- `mode` — default `search`
- `query` — natural-language search/observation intent
- `url` — for `ingest` / fetch
- `layers` — evidence layers to observe

**Returns:** Structured observations with provenance, freshness, and epistemic labels (OBS / DER / INT / SPEC).

**Next step:** `arif_think` or `arif_route`.

---

## 3. arif_think — Reason

**Purpose:** Decompose problems, generate plans, evaluate hypotheses, critique proposals.

**Modes:** `reason` (default) | `reflect` | `verify` | `critique` | `axioms` | `plan` | `plan_review` | `plan_approve` | `refactor_plan` | `metabolize`

**Key params:**
- `mode` — default `reason`
- `query` — the reasoning task
- `plan_id` — for plan review/approve/refactor modes

**Returns:** Structured reasoning output with epistemic labels, facts, inferences, unknowns, confidence bands, and next safe action.

**Next step:** `arif_route` (tool selection) or `arif_judge` (if ready to decide).

---

## 4. arif_route — Direct

**Purpose:** Route natural-language intent to the correct federation organ or kernel tool.

**Modes:** none (single-mode router)

**Key params:**
- `intent` — what you want to accomplish
- `organ` — optional explicit organ override (`arifOS`, `GEOX`, `WEALTH`, `WELL`, `A-FORGE`)
- `organ_tool` — optional direct tool name on the target organ
- `arguments` — optional dict passed to `organ_tool`

**Returns:** Target organ, port, tool prefix, and suggested tools.

**Next step:** Call the routed tool, then `arif_judge` if the action is consequential.

---

## 5. arif_judge — Decide

**Purpose:** Render a binding constitutional verdict.

**Modes:** none (single-mode arbitration gate)

**Required params:**
- `actor` — acting agent identity
- `intent` — what is being proposed
- `requested_capability` — specific capability requested
- `domain` — e.g. `general`, `geox`, `wealth`, `well`, `arifos`
- `reversibility_level` — `FULL` | `PARTIAL` | `NONE`
- `blast_radius` — `none` | `local` | `organ-wide` | `federation-wide` | `irreversible`

**Optional params:**
- `epistemic_state` — default `UNKNOWN`
- `evidence` — list of evidence objects
- `authority_token` — for privileged flows

**Returns:** `SEAL` | `HOLD` | `SABAR` | `VOID`, with violated floors and evidence receipts.

**Next step:** If `SEAL`, call `arif_seal`; if `HOLD`, gather more evidence or escalate to sovereign.

---

## 6. arif_act — Execute

**Purpose:** Execute an approved action through the 900 execution gate.

**Hard requirement:** valid prior SEAL from `arif_judge` → `arif_seal` pipeline.

**Required params:**
- `seal_verdict_id` — SEAL verdict ID
- `approved_action_hash` — hash from the seal

**Optional params:**
- `manifest` — execution manifest (string or object)
- `actor_id`, `session_id`

**Returns:** Execution result with audit receipt.

**Next step:** `arif_seal` the outcome.

---

## 7. arif_seal — Finalize

**Purpose:** Append a verdict or outcome to the immutable VAULT999 ledger.

**Modes:** `seal` (default) | `verify` | `ledger` | `changelog` | `audit`

**Key params:**
- `mode` — default `seal`
- `payload` — verdict/execution payload to anchor
- `ack_irreversible` — required for `seal` mode
- `actor_id`, `actor_signature`, `session_id`, `nonce`

**Returns:** Cryptographic seal receipt with chain integrity status.

**Warning:** Irreversible. Requires explicit `ack_irreversible=true`.

---

## Output Envelope

Every canonical tool returns the same top-level envelope (`CANONICAL_OUTPUT_SCHEMA`):

```json
{
  "status": "OK",
  "tool": "<tool_name>",
  "verdict": "SEAL|HOLD|VOID|SABAR|PROVISIONAL|PARTIAL",
  "result": { /* tool-specific payload */ },
  "meta": { /* actor_id, gate verdicts, audit metadata */ },
  "delta_S": 0.0,
  "timestamp": "2026-07-01T...",
  "session_id": "...",
  "actor_id": "...",
  "output_policy": "DOMAIN_SEAL|DOMAIN_HOLD|DOMAIN_VOID|SIMULATION_ONLY",
  "nine_signal": { /* delta, psi, omega, overall */ },
  "reasons": ["..."],
  "_nine_signal_compliant": true,
  "_violations": []
}
```

---

## Expanded45 Operator Surface (gated)

When `ARIFOS_MCP_EXPOSE_DEV_TOOLS=true`, the following diagnostics are also exposed:

- `arif_canary` — transport/health probe (ping, schema_echo, version_echo, transport_echo, initialize_probe, conformance_report)
- `arif_os_attest` — live kernel self-attestation
- `arif_retrieve_tools` — BM25 lexical tool discovery
- `arif_triage` — session status / preflight
- `arif_compose` — governed response composition
- `arif_conformance_report` — full conformance spine
- `arif_lease_issue` / `arif_lease_inspect` / `arif_lease_revoke` — federation leases
- `arif_heartbeat`, `arif_peer_contract_*`, `arif_detect_*` — organ/institutional probes

These are **not** part of the default public 7-verb facade.

---

*Generated from live `tools/list` on 2026-07-01. DITEMPA BUKAN DIBERI.*
