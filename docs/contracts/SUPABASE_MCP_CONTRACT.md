# Supabase MCP Integration Contract
> **Canonical Source:** `ariffazil/arifOS:docs/contracts/SUPABASE_MCP_CONTRACT.md`
> **Authority:** arifOS F13 SOVEREIGN (Muhammad Arif bin Fazil)
> **Sealed:** 2026-06-02

## 0. The Core Principle

**Do not connect Supabase to MCPs as a router.**
Connect Supabase to MCPs as a **recorder, registry, artifact shelf, and prompt/resource index.**

Every MCP can produce memory.
Only **arifOS** can make it constitutional.
Only **VAULT999** makes it forever.
**AAA** makes it visible.

The Right Connection Model:
```
MCP tool executes
  ↓
arifOS / organ adapter writes receipt
  ↓
Supabase (L4) records:
  - tool call
  - evidence
  - artifact
  - approval
  - verdict
  - seal
  - prompt/resource/tool manifest snapshot
```

Keep writes **fail-soft**. If Supabase fails, the local log keeps the record. Retry later. Supabase should not break GEOX, WEALTH, WELL, or A-FORGE.

---

## 1. Direct vs. Proxy Rule

### Pattern A: Through arifOS → Supabase (High-Risk)
**Who:** arifOS writes for everyone.
**What:** Approvals, judge verdicts, final seals, high-risk tool calls, floor crossings, irreversible actions.
**Why:** Safest constitutional model. If it affects law, judgment, approval, or seal — arifOS writes it.

### Pattern B: Direct Organ → Supabase (Low-Risk)
**Who:** Each organ (GEOX, WEALTH, WELL, A-FORGE) writes its own domain records.
**What:** Low-risk evidence, artifacts, telemetry, manifest snapshots, domain outputs.
**Required Fields for every write:** `organ`, `service_identity`, `tool_name`, `trace_id`, `session_id`, `input_hash`, `output_hash`, `timestamp`.

---

## 2. Table-by-Table Rules

### `arifosmcp_tool_calls`
*   **Who:** arifOS adapter writes canonical tool-call receipts. Organs may write shadow/domain receipts.
*   **What:** Every meaningful MCP tool invocation.
*   **Fields:** `tool_name`, `organ`, `service_ref`, `session_id`, `trace_id`, `risk_tier`, `input_hash`, `output_hash`, `status`, `timestamp`.

### `arifosmcp_approval_tickets`
*   **Who:** arifOS only (or AAA acting as cockpit UI under arifOS rules). No self-approving.
*   **What:** Arif approval required (pending / approved / rejected).

### `arifosmcp_canon_records`
*   **Who:** arifOS, or organs through arifOS-validated adapter.
*   **What:** Evidence-backed facts.
*   **Fields:** `claim_state` (FACT/EST/HYPO/UNK), `evidence_ids`, `source_tool`, `organ`, `confidence`, `timestamp`.

### `arifosmcp_sessions`
*   **Who:** arifOS.
*   **What:** Session opened/closed, summary, outcome, turn_count, linked seals. Do not make Supabase the live session brain.

### `vault_sealed_events` / `vault999_ledger`
*   **Who:** arifOS / VAULT999 service only.
*   **What:** Final truth. Organs propose; arifOS seals.

### `artifacts`
*   **Who:** The organ that creates the artifact.
*   **What:** Artifact metadata (e.g., `geox-artifacts`). Sealed artifacts need arifOS/VAULT999 seal linkage.

### `mcp_prompt_versions`
*   **Who:** All organs.
*   **What:** Prompt metadata and versions. Do not blindly dump secret prompts with credentials.
*   **Fields:** `prompt_id`, `organ`, `tool_name`, `prompt_name`, `version`, `content_hash`, `storage_path`, `active`, `created_at`, `created_by`, `risk_notes`.

### `mcp_resources`
*   **What:** Resource metadata (toolcards, schemas, playbooks, ontologies).
*   **Fields:** `resource_id`, `organ`, `resource_type`, `name`, `uri_or_path`, `content_hash`, `version`, `storage_bucket`, `storage_path`, `active`, `created_at`.

### `mcp_manifest_snapshots`
*   **What:** Periodic snapshots of server identity, tool count/names, schemas, risk tiers, hash. Allows AAA to monitor surface drift.

---

## 3. Recommended Connection Paths per Organ

*   **arifOS (Governance):** Writes `tool_calls`, `approval_tickets`, `canon_records`, `sessions`, `floor_rules`, `vault_sealed_events`, `vault999_ledger`, `judge_verdicts`.
*   **GEOX (Earth):** Writes domain evidence and artifacts (`tool_calls`, `canon_records`, `evidence_items`, `artifacts`, `manifest_snapshots`). Final verdict/seal via arifOS.
*   **WEALTH (Capital):** Writes `portfolio_snapshots`, `transactions`, `tool_calls`, `canon_records`, `artifacts`, `manifest_snapshots`. High-consequence capital action via arifOS.
*   **WELL (Vitality):** Writes `well_states`, `agent_telemetry`, `canon_records`, `tool_calls`, `manifest_snapshots`. WELL reflects; arifOS decides.
*   **A-FORGE (Execution):** Writes `tool_calls`, `artifacts`, `canon_records`. `approval_tickets` only if delegated. `vault_sealed_events` only after arifOS seal. No self-authorization for Tier 3.
*   **AAA (Identity/Cockpit):** Mostly reads (`pending_approvals`, `recent_seals`, `mcp_surface`, `evidence_index`, etc.). May write UI acknowledgement, approval actions, dashboard notes under arifOS rules.

---

## 4. The Unified Adapter
Organs can use a shared adapter library implementing:
`record_tool_call()`, `record_evidence()`, `record_artifact()`, `record_manifest_snapshot()`, `record_canon_record()`, `record_approval_ticket()`, `record_judge_verdict()`, `seal_vault999()`.

Permissions must be enforced:
*   GEOX can record evidence, but cannot final-seal truth.
*   A-FORGE can record artifacts, but cannot self-approve Tier 3.
*   AAA can submit approval, but cannot fake it.
*   arifOS can judge and seal.
