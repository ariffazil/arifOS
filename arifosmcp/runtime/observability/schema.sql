-- arifOS Observability Schema
-- Forges a sovereign telemetry store in Postgres.
-- Migration: psql -d arifos -f schema.sql
-- Idempotent — safe to re-run.

CREATE SCHEMA IF NOT EXISTS observability;

-- ── Core observations table ────────────────────────────────────────────
-- Every arif_* tool call becomes one row. Single-table MVP.
-- Decompose into traces/spans/events/scores when volume > 500k/month.

CREATE TABLE IF NOT EXISTS observability.observations (
    id              UUID PRIMARY KEY,
    trace_id        UUID NOT NULL,
    span_id         UUID NOT NULL,
    parent_span_id  UUID,
    session_id      TEXT,
    actor_id        TEXT NOT NULL DEFAULT 'unknown',
    tool_name       TEXT NOT NULL DEFAULT '',
    organ_id        TEXT,
    verdict_class   TEXT NOT NULL DEFAULT 'OK',
    delta_s         DOUBLE PRECISION DEFAULT 0,
    reasons         JSONB,
    next_safe_action TEXT,
    uncertainty_tag TEXT,
    input_hash      TEXT,
    output_hash     TEXT,
    vault_receipt   TEXT,
    cost_usd        DOUBLE PRECISION,
    model_name      TEXT,
    latency_ms      DOUBLE PRECISION,
    start_time      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    end_time        TIMESTAMPTZ,
    metadata        JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Query indexes ─────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_obs_trace_id
    ON observability.observations (trace_id);

CREATE INDEX IF NOT EXISTS idx_obs_actor_id
    ON observability.observations (actor_id);

CREATE INDEX IF NOT EXISTS idx_obs_tool_name
    ON observability.observations (tool_name);

CREATE INDEX IF NOT EXISTS idx_obs_created_at
    ON observability.observations (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_obs_session_id
    ON observability.observations (session_id);

CREATE INDEX IF NOT EXISTS idx_obs_verdict
    ON observability.observations (verdict_class);

-- ── Retention ─────────────────────────────────────────────────────────
-- Observations older than 90 days can be archived to MinIO and pruned.
-- Add a cron job later: DELETE FROM observability.observations
--   WHERE created_at < NOW() - INTERVAL '90 days';
