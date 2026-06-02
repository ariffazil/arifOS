-- ============================================================
-- Unified AAA Read Layer
-- Reads from both production (public.arifosmcp_*) and
-- Phase 1 design (s000/s999) namespaces.
--
-- Rules:
-- - Where schemas align, UNION both with type-safe casting
-- - Where schemas differ, keep separate and label clearly
-- - Production vault (vault_sealed_events) stays separate from design v2
-- - AAA reads one clean picture regardless of source
-- ============================================================

-- Drop existing views first
DROP VIEW IF EXISTS aaa.unified_tool_calls CASCADE;
DROP VIEW IF EXISTS aaa.unified_approvals CASCADE;
DROP VIEW IF EXISTS aaa.unified_evidence CASCADE;
DROP VIEW IF EXISTS aaa.unified_floor_rules CASCADE;
DROP VIEW IF EXISTS aaa.unified_artifacts CASCADE;
DROP VIEW IF EXISTS aaa.unified_mcp_servers CASCADE;
DROP VIEW IF EXISTS aaa.vault_ledger_production CASCADE;
DROP VIEW IF EXISTS aaa.vault_ledger_design CASCADE;
DROP VIEW IF EXISTS aaa.recent_all_seals CASCADE;
DROP VIEW IF EXISTS aaa.namespace_summary CASCADE;

-- 1. UNIFIED TOOL_CALLS
-- Both namespaces have tool_calls with similar structure
CREATE OR REPLACE VIEW aaa.unified_tool_calls AS
SELECT
    'production' AS source,
    id::text AS call_id,
    organ AS organ_code,
    session_id AS session_ref,
    tool_name,
    agent_id AS actor_ref,
    verdict,
    floor_triggered,
    duration_ms AS latency_ms,
    epoch AS created_at,
    result_code,
    peace2::text,
    error_msg,
    NULL::text AS arguments,       -- production has no raw args
    NULL::text AS result,          -- production has no raw result
    NULL::integer AS risk_tier,
    NULL::text AS status,
    -- AAA namespace receipt fields (added 2026-06-02)
    COALESCE(aaa_surface, 'AAA-HF') AS aaa_surface,
    aaa_doctrine_version,
    aaa_canon_refs,
    floor_refs,
    COALESCE(record_class, 'constitutional_receipt') AS record_class
FROM public.arifosmcp_tool_calls
UNION ALL
SELECT
    'design' AS source,
    tool_call_id AS call_id,
    organ_code,
    session_ref,
    tool_name,
    actor_ref,
    NULL::text AS verdict,
    NULL::text AS floor_triggered,
    latency_ms,
    created_at,
    NULL::text AS result_code,
    NULL::text AS peace2,
    NULL::text AS error_msg,
    arguments::text AS arguments,   -- jsonb cast to text
    result::text AS result,
    risk_tier,
    status,
    -- AAA namespace receipt fields (NULL-filled for design namespace)
    'AAA-HF'::text AS aaa_surface,
    NULL::text AS aaa_doctrine_version,
    NULL::text[] AS aaa_canon_refs,
    NULL::text[] AS floor_refs,
    'constitutional_receipt'::text AS record_class
FROM s000.tool_calls;

-- 2. UNIFIED APPROVALS
-- Production: ticket model (action_plan, human_verdict)
-- Design: receipt model (reason, status)
CREATE OR REPLACE VIEW aaa.unified_approvals AS
SELECT
    'production' AS source,
    ticket_id::text AS approval_id,
    'ticket' AS approval_form,
    action_plan::text AS reason,
    human_verdict::text AS verdict,
    requested_at AS created_at,
    resolved_at AS decided_at,
    NULL::text AS session_ref,
    NULL::text AS tool_name,
    NULL::text AS requested_by_ref,
    NULL::text AS approved_by_ref,
    NULL::text AS status,
    NULL::text AS signed_payload
FROM public.arifosmcp_approval_tickets
UNION ALL
SELECT
    'design' AS source,
    approval_id,
    'receipt' AS approval_form,
    reason::text,
    status AS verdict,
    created_at,
    decided_at,
    NULL::text AS session_ref,
    NULL::text AS tool_name,
    requested_by_ref,
    approved_by_ref,
    status,
    signed_payload::text
FROM s000.approvals;

-- 3. UNIFIED EVIDENCE
-- Production: canon_records (body jsonb, record_type)
-- Design: evidence_items (content text, claim_state)
CREATE OR REPLACE VIEW aaa.unified_evidence AS
SELECT
    'production' AS source,
    id::text AS evidence_id,
    record_type::text AS claim_type,
    reference_id::text AS source_ref,
    body::text AS content,
    verdict::text AS trust_verdict,
    witness::text AS witness_ref,
    sealed_by::text AS authority_ref,
    epoch AS created_at,
    NULL::text AS session_ref,
    NULL::text AS organ_code,
    NULL::text AS source_type,
    NULL::text AS title,
    NULL::float AS confidence,
    NULL::text AS metadata
FROM public.arifosmcp_canon_records
UNION ALL
SELECT
    'design' AS source,
    evidence_id,
    claim_state::text AS claim_type,
    source_uri::text AS source_ref,
    content::text,
    NULL::text AS trust_verdict,
    NULL::text AS witness_ref,
    NULL::text AS authority_ref,
    created_at,
    session_ref,
    organ_code,
    source_type,
    title,
    confidence,
    metadata::text
FROM s000.evidence_items;

-- 4. UNIFIED FLOOR RULES (F1-F13 constitutional)
CREATE OR REPLACE VIEW aaa.unified_floor_rules AS
SELECT
    'production' AS source,
    floor_code::text AS floor_id,
    rule_name::text AS floor_name,
    constraint_definition::text,
    is_active,
    updated_at,
    NULL::text AS domain,
    NULL::text AS enforcement_level
FROM public.arifosmcp_floor_rules
UNION ALL
SELECT
    'design' AS source,
    id::text AS floor_id,
    name::text AS floor_name,
    invariant::text,
    active AS is_active,
    created_at,
    domain,
    enforcement_level
FROM s000.constitutional_floors;

-- 5. UNIFIED ARTIFACTS (design only for now)
CREATE OR REPLACE VIEW aaa.unified_artifacts AS
SELECT
    'design' AS source,
    artifact_id,
    session_ref,
    organ_code,
    bucket,
    path,
    filename,
    mime_type,
    size_bytes,
    content_hash,
    artifact_type,
    claim_state,
    created_at
FROM s000.artifacts;

-- 6. UNIFIED MCP SERVERS (design only)
CREATE OR REPLACE VIEW aaa.unified_mcp_servers AS
SELECT
    'design' AS source,
    server_ref,
    organ_code,
    name AS server_name,
    endpoint_url,
    local_port,
    transport,
    authority_role,
    status_snapshot,
    source_of_truth,
    last_observed_at,
    created_at
FROM s000.mcp_servers;

-- 7. VAULT LEDGER — production (L6 mirror)
CREATE OR REPLACE VIEW aaa.vault_ledger_production AS
SELECT
    'production' AS source,
    event_id::text AS seal_id,
    event_type::text AS seal_type,
    session_id,
    actor_id::text AS signed_by_ref,
    stage::text,
    verdict::text,
    risk_tier::text AS risk_tier,
    payload::text AS content_preview,
    source_ledger::text,
    prev_leaf::text AS previous_hash,
    merkle_leaf::text AS content_hash,
    signature::text,
    sealed_at,
    created_at
FROM public.vault_sealed_events
ORDER BY created_at DESC;

-- 8. VAULT LEDGER — design v2
CREATE OR REPLACE VIEW aaa.vault_ledger_design AS
SELECT
    'design' AS source,
    seal_id::text,
    session_ref,
    subject_type::text,
    subject_ref::text,
    seal_type::text,
    verdict::text,
    content_hash::text,
    previous_hash::text,
    content::text AS content_preview,
    signature::text,
    signed_by_ref::text AS signed_by_ref,
    created_at
FROM s999.vault999_ledger
ORDER BY created_at DESC;

-- 9. RECENT ALL SEALS — combined both ledgers
CREATE OR REPLACE VIEW aaa.recent_all_seals AS
SELECT
    'production' AS source,
    event_id::text AS seal_id,
    event_type::text AS seal_type,
    session_id::text,
    actor_id::text AS signed_by_ref,
    verdict::text,
    risk_tier::text AS risk_tier,
    merkle_leaf::text AS content_hash,
    sealed_at AS created_at
FROM public.vault_sealed_events
UNION ALL
SELECT
    'design' AS source,
    seal_id::text,
    session_ref::text,
    NULL::text,
    signed_by_ref::text,
    verdict::text,
    NULL::text AS risk_tier,
    content_hash::text,
    created_at
FROM s999.vault999_ledger
ORDER BY created_at DESC;

-- 10. NAMESPACE SUMMARY — row counts across both namespaces
CREATE OR REPLACE VIEW aaa.namespace_summary AS
SELECT 'production' AS namespace, 'arifosmcp_tool_calls' AS table_name, COUNT(*)::int AS row_count, 'trusted production — empty until MCP kernel integration' AS note FROM public.arifosmcp_tool_calls
UNION ALL SELECT 'production', 'arifosmcp_approval_tickets', COUNT(*)::int, 'trusted production ticket model' FROM public.arifosmcp_approval_tickets
UNION ALL SELECT 'production', 'arifosmcp_canon_records', COUNT(*)::int, 'trusted production — may be empty' FROM public.arifosmcp_canon_records
UNION ALL SELECT 'production', 'vault_sealed_events', COUNT(*)::int, 'canonical L6 — 1,337 sealed events' FROM public.vault_sealed_events
UNION ALL SELECT 'production', 'vault_outcomes', COUNT(*)::int, 'existing outcomes' FROM public.vault_outcomes
UNION ALL SELECT 'production', 'arifosmcp_floor_rules', COUNT(*)::int, 'F1-F13 seeded rules' FROM public.arifosmcp_floor_rules
UNION ALL SELECT 'design', 's000.tool_calls', COUNT(*)::int, 'Phase 1 design — smoke test rows' FROM s000.tool_calls
UNION ALL SELECT 'design', 's000.approvals', COUNT(*)::int, 'Phase 1 design — smoke test rows' FROM s000.approvals
UNION ALL SELECT 'design', 's000.evidence_items', COUNT(*)::int, 'Phase 1 design — smoke test rows' FROM s000.evidence_items
UNION ALL SELECT 'design', 's000.artifacts', COUNT(*)::int, 'Phase 1 design — smoke test rows' FROM s000.artifacts
UNION ALL SELECT 'design', 's999.vault999_ledger', COUNT(*)::int, 'Phase 1 v2 ledger — 9 smoke test rows' FROM s999.vault999_ledger
UNION ALL SELECT 'design', 's000.judge_verdicts', COUNT(*)::int, 'Phase 1 design — smoke test rows' FROM s000.judge_verdicts;
