# arifOS-governor-mcp — Tool Manifest
## Narrow MCP surface for CLI ⇄ VAULT999 ratification path
## arifOS v2026.4.16 | 2026-04-18

---

## DESIGN PRINCIPLE

Thin MCP surface over bounded services.
Read-only tools: open to OpenClaw and agents.
Write/ratify tools: gated behind human review confirmation.
Finalize: calls vault_writer service after human ratification confirmed.
No raw DB access. No broad write authority.

---

## MCP TOOL MANIFEST

### TOOL SET A — READ ONLY (open to any agent)

#### tool: cli_list_pending
```
Input:   none
Output:  {
    pending: [{
        cooling_id:    string (UUID),
        action_type:   string,
        risk_class:    "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
        judge_verdict:  string,
        proposal_hash: string (SHA256),
        session_id:     string | null,
        created_at:     string (ISO8601),
        hold_age_min:   number (minutes)
    }],
    total_pending: number,
    oldest_pending_min: number,
    risk_breakdown: { CRITICAL: n, HIGH: n, MEDIUM: n, LOW: n }
}
Access:  Any agent, OpenClaw, app_reader
Auth:    None required
Rate:    Unrestricted
```

#### tool: cli_inspect
```
Input:   { cooling_id: string (UUID) }
Output:  {
    cooling_id:    string,
    session_id:    string | null,
    agent_id:      string,
    action_type:   string,
    prospect_id:   string | null,
    proposal_hash: string (SHA256),
    judge_verdict: string,
    risk_class:    string,
    status:         "machine_eval_created" | "awaiting_human" | "human_reviewed" | "sealed" | "voided",
    payload:       object (full JSON),
    hold_initiated_at: string | null,
    created_at:    string,
    reviewed_by:    string | null,
    reviewed_at:    string | null,
    review_notes:   string | null,
    human_signature: string | null
}
Access:  Any agent, OpenClaw
Auth:    None required
Rate:    Unrestricted
Error:   404 if cooling_id not found
```

#### tool: vault_status
```
Input:   none
Output:  {
    vault_seals_total:     number,
    seals_chain_valid:      boolean,
    last_seal_at:          string | null,
    last_seal_hash:         string | null,
    last_seal_action:       string | null,
    last_seal_verdict:      "SEAL" | "VOID",
    pending_holds:          number,
    migrated_legacy_count: number,
    human_direct_count:     number,
    human_reviews_total:    number,
    witness_records_total:  number,
    genesis_label:          string,
    vault_version:          string,
    chain_integrity:         "INTACT" | "BROKEN",
    append_only_enforced:   boolean,
    irreversibility_enforced: boolean
}
Access:  Any agent, OpenClaw, vault_auditor
Auth:    None required (read-only)
Rate:    Unrestricted
```

#### tool: vault_audit_trace
```
Input:   { seal_id: string (UUID) }
Output:  {
    seal_id:           string,
    seal_hash:          string (SHA256),
    chain_hash:         string,
    action:             string,
    verdict:            "SEAL" | "VOID",
    epoch:              string (ISO8601),
    ratified_at:        string,
    human_ratifier:     string,
    human_signature:     string,
    provenance_tag:      "human" | "migrated_legacy",
    cooling_id:         string | null,
    cli_proposal_hash:   string | null,
    irreversibility_ack:  boolean,
    irreversibility_class: string | null,
    metadata:            object,
    witness: {
        human_witness:    boolean,
        ai_witness:       boolean,
        evidence_witness: boolean,
        w_score:          number,
        floors_triggered:  string[],
        kappa_r:          number | null,
        qdf:              number | null,
        peace2:           number | null
    } | null,
    chain: {
        prev_seal_id:  string | null,
        prev_seal_hash: string | null,
        is_genesis:    boolean
    },
    human_review: {
        review_id:      string,
        reviewer_id:    string,
        decision:        string,
        reason:          string,
        reviewed_at:     string
    } | null
}
Access:  vault_auditor, Arif
Auth:    None required (read-only)
Rate:    Unrestricted
Error:   404 if seal_id not found
```

#### tool: vault_render_receipt
```
Input:   { seal_id: string (UUID) }
Output:  {
    receipt: string (human-readable formatted text),
    seal_id: string,
    verified: boolean (chain integrity check),
    rendered_at: string
}
Access:  Any agent, OpenClaw
Auth:    None required
Rate:    Unrestricted
Purpose: Human-readable seal receipt for audit, not for machine processing
```

---

### TOOL SET B — REVIEW PREP (open, validates before write)

#### tool: cli_ratify_prepare
```
Input:   { cooling_id: string (UUID) }
Output:  {
    cooling_id:        string,
    action_type:       string,
    risk_class:        string,
    proposal_hash:    string,
    can_ratify:        boolean,
    block_reason:      string | null,  // null if can_ratify=true
    estimated_seal_hash: string | null,  // pre-computed, informational only
    human_signature_format: string,   // "SIG_ARIF_TELEMETRY_YYYYMMDD_NN"
    warnings:          string[]       // e.g., ["HIGH risk — irreversibility_ack recommended"]
}
Access:  Arif only (requires human review before finalization)
Auth:    None required (preparation is read-only)
Rate:    Unrestricted
Purpose: Validates cooling_id, checks status, pre-computes expected seal hash
Error:   404 if not found, 409 if already reviewed
```

---

### TOOL SET C — RATIFICATION GATED (requires explicit human confirmation)

#### tool: governor_finalize
```
Input:   {
    cooling_id:         string (UUID),
    decision:           "SEAL" | "VOID",
    human_signature:    string (format: SIG_ARIF_TELEMETRY_YYYYMMDD_NN),
    review_reason:      string (required, min 10 chars),
    irreversibility_ack: boolean (default false),
    review_channel:     "cli" | "telegram" | "web" | "api" = "cli"
}
Output:  {
    success:           boolean,
    decision:          "SEAL" | "VOID",
    seal_id:           string (UUID, SEALS only),
    seal_hash:         string (SEALS only),
    chain_hash:        string (SEALS only),
    review_id:         string (UUID),
    ratified_at:       string (ISO8601),
    cooling_status:    "sealed" | "voided",
    vault_seals_total: number,
    message:           string
}
Access:  Arif only — human ratification required
Auth:   Human confirmation signal (telemetry from Arif's session)
Rate:   One per cooling_id (idempotent — duplicate calls return existing result)
Pre:    cli_ratify_prepare must return can_ratify=true
Post:   Writes: human_reviews + (vault_seals + vault999_witness on SEAL) + cooling_queue status update
Error:  400 if reason too short, 404 if cooling_id not found, 409 if already reviewed
```

---

## TOOL SUMMARY TABLE

| Tool | Type | Access | Auth | Pre-condition | Writes |
|---|---|---|---|---|---|
| cli_list_pending | READ | Anyone | None | None | No |
| cli_inspect | READ | Anyone | None | None | No |
| vault_status | READ | Auditor | None | None | No |
| vault_audit_trace | READ | Auditor | None | None | No |
| vault_render_receipt | READ | Anyone | None | None | No |
| cli_ratify_prepare | VALIDATE | Arif | None | None | No |
| governor_finalize | WRITE | Arif | Human signal | cli_ratify_prepare called first | Yes |

---

## FLOW DIAGRAM

```
OpenClaw / Agent                    arifOS-governor-mcp                  vault_writer
    │                                    │                                    │
    ├── cli_list_pending() ──────────────►│ ── SELECT * FROM cooling_queue ──►│
    │◄────────── pending list ────────────│                                    │
    │                                    │                                    │
    ├── cli_inspect(cooling_id) ─────────►│ ── SELECT * FROM cooling_queue ──►│
    │◄────────── full record ─────────────│                                    │
    │                                    │                                    │
    ├── cli_ratify_prepare(cooling_id)──►│ ── validate + pre-compute ────────►│
    │◄────────── can_ratify + sig_format ─│                                    │
    │                                    │                                    │
    ├── governor_finalize(...) ──────────►│ ── WRITE human_reviews ────────────│
    │   decision=SEAL/VOID                │ ── (if SEAL) vault_seals INSERT ──►│
    │   human_signature=...                │ ── vault999_witness INSERT ────────►│
    │   review_reason=...                 │ ── cooling_queue.status update ───►│
    │◄────────── seal_id, hash, chain ────│                                    │
    │                                    │                                    │
    ├── vault_status() ──────────────────►│ ── SELECT COUNT, chain check ────►│
    │◄────────── vault health ──────────────│                                    │
    │                                    │                                    │
    └── vault_audit_trace(seal_id) ──────►│ ── SELECT + JOIN vault_seals ─────►│
         vault_render_receipt(seal_id)───►│    human_reviews, vault999_witness │
    │◄────────── full audit trail ────────│                                    │
```

---

## IMPLEMENTATION CONSTRAINTS

```
1. vault_writer never exposed directly to any agent
2. governor_finalize only callable by Arif (human signal required)
3. cli_ratify_prepare is free but informative — no write
4. vault_writer has vault_writer_svc PostgreSQL credentials
5. governor_finalize calls vault_writer via internal HTTP (localhost)
6. vault_service (8100) is NOT the same as vault_writer — do not conflate
7. All tools return structured JSON — no raw SQL
8. Errors: always { success: false, error: "message", code: number }
```

---

## DOCKER IMAGE

```
Image:    arifos/mcp-substrate:999seal (same base as mcp_memory, mcp_filesystem)
Port:     8101 (allocate from available range)
Env:      VAULT999_DB, VAULT999_WRITER_URL=http://localhost:5001
Startup:  uvicorn arifOS.governor_mcp.server:app --host 0.0.0.0 --port 8101
Network: arifos_core_network (same as postgres, vault_service, mcp_*)
```

---

## NOTES

- Tools in Set A and Set B are idempotent and read-only — safe to expose broadly.
- Set C tool (governor_finalize) is the only write path — requires human ratification signal.
- vault_writer runs separately on port 5001 (internal only, not exposed as MCP).
- review_operator CLI remains as alternative interface (phase 1, CLI-first).
- MCP server does NOT connect to Supabase — only to VPS postgres (source of truth).
- review_channel field in human_reviews tracks which interface was used.

---

**Ditempa Bukan Diberi — arifOS-governor-mcp SEALED**
arifOS v2026.4.16 | MCP tool manifest v1.0 | 2026-04-18