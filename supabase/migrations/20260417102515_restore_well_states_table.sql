-- WELL state: persistent agent/session state
-- Specifically for biological telemetry (Sleep, Stress, Cognitive Load)
CREATE TABLE IF NOT EXISTS arifosmcp_well_states (
  id            BIGSERIAL PRIMARY KEY,
  agent_id      TEXT NOT NULL,
  state_key     TEXT NOT NULL,
  state_value   JSONB NOT NULL DEFAULT '{}',
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(agent_id, state_key)
);

CREATE INDEX IF NOT EXISTS idx_well_states_agent ON arifosmcp_well_states(agent_id);
