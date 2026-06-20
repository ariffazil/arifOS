-- ============================================================
-- Migration: 20260620_001_kernel_state.sql
-- PURPOSE: Single authoritative kernel health source for all attestation endpoints
-- Type: Additive. No existing tables altered.
-- Rollback: DROP TABLE IF EXISTS public.arifosmcp_kernel_state;
-- Introduced: 2026-06-20 Phase 1 truth unification
-- ============================================================

-- 1. Create the single-truth table
CREATE TABLE IF NOT EXISTS public.arifosmcp_kernel_state (
  id                   bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  kernel_version       text NOT NULL,
  constitution_hash    text NOT NULL DEFAULT 'UNSET',
  schema_hash          text NOT NULL DEFAULT 'UNSET',
  tool_count_canonical integer NOT NULL DEFAULT 0,
  tool_count_live      integer NOT NULL DEFAULT 0,
  organ_count          integer NOT NULL DEFAULT 0,
  failed_calls_24h     integer NOT NULL DEFAULT 0,
  kernel_status        text NOT NULL DEFAULT 'UNKNOWN'
                         CHECK (kernel_status IN ('ALIVE','DEGRADED','HALTED','BOOTSTRAPPING')),
  degradation_reason   text,
  organ_status         jsonb NOT NULL DEFAULT '{}'::jsonb,
  declared_tools       jsonb NOT NULL DEFAULT '{}'::jsonb,
  live_tools           jsonb NOT NULL DEFAULT '{}'::jsonb,
  peer_contract_hash   text,
  last_refreshed_at    timestamptz NOT NULL DEFAULT now(),
  sealed_by            text NOT NULL DEFAULT 'fn_kernel_state_refresh',
  seal_id              text
);

-- 2. RLS: service_role full access, authenticated read-only, anon blocked
ALTER TABLE public.arifosmcp_kernel_state ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_full" ON public.arifosmcp_kernel_state
  FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_read" ON public.arifosmcp_kernel_state
  FOR SELECT TO authenticated USING (true);

-- 3. Seed the initial row
INSERT INTO public.arifosmcp_kernel_state (
  kernel_version, tool_count_canonical, tool_count_live,
  kernel_status, declared_tools, sealed_by
) VALUES (
  'v2026.05.05-SSCT', 13, 0,
  'BOOTSTRAPPING',
  '{"arifos":13,"wealth":20,"geox":37,"well":17,"aforge":8,"aaa":4,"apex":2}'::jsonb,
  'claude_forge_initial_seed'
);

COMMENT ON TABLE public.arifosmcp_kernel_state IS
  'arifOS single authoritative kernel health source. All attestation endpoints MUST read from this table. '
  'No endpoint may compute health independently. Updated by refresh_kernel_state() only. '
  'Introduced: 2026-06-20 Phase 1 truth unification.';
