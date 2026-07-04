-- ============================================================
-- Cooling Ledger Core Schema
-- ============================================================
-- AI's governed short-term memory with temperature decay,
-- verdict states, tri-witness, principal overrides, and
-- promotion into Vault999.
--
-- Storage model:
--   Cooling Ledger = Postgres (fast, queryable, metabolic)
--   Vault999       = filesystem JSONL (append-only, immutable)
--
-- Author: FORGE (A-FORGE execution arm)
-- Date:   2026-06-28
-- ============================================================

-- ─────────────────────────────────────────────────────────
-- SCHEMA: cooling_ledger
-- ─────────────────────────────────────────────────────────
CREATE SCHEMA IF NOT EXISTS cooling_ledger;

-- ─────────────────────────────────────────────────────────
-- TABLE 1: cooling_ledger_entries
-- The AI's governed short-term notebook.
-- Every line has: temperature, verdict, risk, witness, timer.
-- ─────────────────────────────────────────────────────────
CREATE TABLE cooling_ledger_entries (
    id                uuid        NOT NULL DEFAULT gen_random_uuid(),
    epoch             timestamptz NOT NULL DEFAULT now(),
    organ             text        NOT NULL,          -- which organ wrote this: arifos, aforge, geox, wealth, well, etc.
    entry_type        text        NOT NULL,          -- evidence | reasoning | verdict_pending | override | failure | witness | seal_ready
    payload           jsonb       NOT NULL DEFAULT '{}',  -- the actual content: what was seen, thought, decided

    -- Verdict state machine
    verdict_state     text        NOT NULL DEFAULT 'PENDING'
                         CHECK (verdict_state IN (
                             'PENDING', 'HOLD', 'SABAR',
                             'VOID', 'SEAL_READY', 'SEALED'
                         )),

    -- Metabolic signals
    temperature       float8      NOT NULL DEFAULT 1.0,  -- 1.0 = fresh, 0.0 = fully cooled
    risk_score        float8      NOT NULL DEFAULT 0.0,  -- 0.0 = safe, 1.0 = dangerous
    decay_tier        text        NOT NULL DEFAULT 'HOT'
                         CHECK (decay_tier IN ('HOT', 'WARM', 'COOL', 'FROZEN', 'ERASED')),

    -- Provenance
    principal_id      text,                               -- who (human principal)
    agent_role        text,                               -- which agent wrote this
    lease_id          text,                               -- which lease authorized this entry
    session_id        text,                               -- which constitutional session

    -- Timestamps
    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz NOT NULL DEFAULT now(),
    cooled_at         timestamptz,                        -- when temperature hit 0
    promoted_at       timestamptz,                        -- when promoted to vault999

    -- Soft delete (never hard-delete from Cooling Ledger)
    deleted_at        timestamptz,

    CONSTRAINT pk_cooling_ledger_entries PRIMARY KEY (id)
);

-- Indexes for fast metabolic queries
CREATE INDEX idx_cle_organ             ON cooling_ledger_entries(organ);
CREATE INDEX idx_cle_entry_type         ON cooling_ledger_entries(entry_type);
CREATE INDEX idx_cle_verdict_state      ON cooling_ledger_entries(verdict_state);
CREATE INDEX idx_cle_temperature        ON cooling_ledger_entries(temperature);
CREATE INDEX idx_cle_decay_tier         ON cooling_ledger_entries(decay_tier);
CREATE INDEX idx_cle_created_at         ON cooling_ledger_entries(created_at DESC);
CREATE INDEX idx_cle_principal_id       ON cooling_ledger_entries(principal_id);
CREATE INDEX idx_cle_session_id         ON cooling_ledger_entries(session_id);
CREATE INDEX idx_cle_risk_score         ON cooling_ledger_entries(risk_score DESC)
                         WHERE deleted_at IS NULL;

-- Composite index for decay queries
CREATE INDEX idx_cle_decay_candidate
    ON cooling_ledger_entries(temperature, created_at)
    WHERE deleted_at IS NULL AND verdict_state NOT IN ('SEAL_READY', 'SEALED');

COMMENT ON TABLE cooling_ledger_entries IS
    'AI governed short-term memory. Every entry has temperature, verdict, risk, witness, timer.';


-- ─────────────────────────────────────────────────────────
-- TABLE 2: cooling_decay_events
-- Log of every temperature change event.
-- Audit trail for how the AI's memory cools over time.
-- ─────────────────────────────────────────────────────────
CREATE TABLE cooling_decay_events (
    id                uuid        NOT NULL DEFAULT gen_random_uuid(),
    entry_id          uuid        NOT NULL
                         REFERENCES cooling_ledger_entries(id)
                         ON DELETE CASCADE,
    old_temperature   float8      NOT NULL,
    new_temperature   float8      NOT NULL,
    old_tier          text,
    new_tier          text,
    decay_reason      text        NOT NULL
                         CHECK (decay_reason IN (
                             'age', 'reference', 'verdict',
                             'override', 'manual', 'promotion', 'reheat'
                         )),
    triggered_by      text,                              -- principal_id or 'kernel' or 'auto'
    metadata          jsonb       NOT NULL DEFAULT '{}',
    created_at        timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT pk_cooling_decay_events PRIMARY KEY (id)
);

CREATE INDEX idx_cde_entry_id   ON cooling_decay_events(entry_id);
CREATE INDEX idx_cde_created_at ON cooling_decay_events(created_at DESC);
CREATE INDEX idx_cde_decay_reason ON cooling_decay_events(decay_reason);

COMMENT ON TABLE cooling_decay_events IS
    'Audit log of every temperature decay event in the Cooling Ledger.';


-- ─────────────────────────────────────────────────────────
-- TABLE 3: witness_signatures
-- Tri-witness: human + agent + external log.
-- Makes reality non-deniable.
-- ─────────────────────────────────────────────────────────
CREATE TABLE witness_signatures (
    id                uuid        NOT NULL DEFAULT gen_random_uuid(),
    entry_id          uuid        NOT NULL
                         REFERENCES cooling_ledger_entries(id)
                         ON DELETE CASCADE,
    witness_type      text        NOT NULL
                         CHECK (witness_type IN ('human', 'agent', 'external')),
    witness_id        text        NOT NULL,              -- principal_id | agent_role | external_system_id
    signature_hash    text        NOT NULL,              -- cryptographic proof this witness saw it
    metadata          jsonb       NOT NULL DEFAULT '{}',
    created_at        timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT pk_witness_signatures PRIMARY KEY (id)
);

CREATE INDEX idx_ws_entry_id     ON witness_signatures(entry_id);
CREATE INDEX idx_ws_witness_id  ON witness_signatures(witness_id);
CREATE INDEX idx_ws_witness_type ON witness_signatures(witness_type);

COMMENT ON TABLE witness_signatures IS
    'Tri-witness signatures (human + agent + external) for non-repudiation.';


-- ─────────────────────────────────────────────────────────
-- TABLE 4: override_actions
-- Every principal override: freeze, reheat, accelerate.
-- Unlimited override = human tyranny. Budget enforces balance.
-- ─────────────────────────────────────────────────────────
CREATE TABLE override_actions (
    id                uuid        NOT NULL DEFAULT gen_random_uuid(),
    entry_id          uuid        NOT NULL
                         REFERENCES cooling_ledger_entries(id)
                         ON DELETE CASCADE,
    principal_id      text        NOT NULL,              -- who overrode
    action            text        NOT NULL
                         CHECK (action IN ('freeze', 'reheat', 'accelerate', 'void', 'promote')),
    justification_hash text       NOT NULL,              -- hash of why this override happened
    justification_text text,                           -- human-readable reason (not stored in vault)
    metadata          jsonb       NOT NULL DEFAULT '{}',
    created_at        timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT pk_override_actions PRIMARY KEY (id)
);

CREATE INDEX idx_oa_entry_id     ON override_actions(entry_id);
CREATE INDEX idx_oa_principal_id ON override_actions(principal_id);
CREATE INDEX idx_oa_action      ON override_actions(action);
CREATE INDEX idx_oa_created_at  ON override_actions(created_at DESC);

COMMENT ON TABLE override_actions IS
    'Principal override actions with justification hashes. Budget-enforced.';


-- ─────────────────────────────────────────────────────────
-- TABLE 5: vault_promotions
-- Record of every entry promoted from Cooling Ledger → Vault999.
-- Once promoted: permanent, immutable, identity-defining.
-- ─────────────────────────────────────────────────────────
CREATE TABLE vault_promotions (
    id                uuid        NOT NULL DEFAULT gen_random_uuid(),
    entry_id          uuid        NOT NULL
                         REFERENCES cooling_ledger_entries(id)
                         ON DELETE SET NULL,  -- entry may be deleted after promotion
    vault_path        text        NOT NULL,   -- path in Vault999 filesystem
    seal_hash         text        NOT NULL,   -- hash of sealed record
    promoted_by       text        NOT NULL,   -- principal_id or 'kernel'
    promotion_reason  text,                  -- why this was worth sealing
    metadata          jsonb       NOT NULL DEFAULT '{}',
    created_at        timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT pk_vault_promotions PRIMARY KEY (id)
);

CREATE INDEX idx_vp_entry_id    ON vault_promotions(entry_id);
CREATE INDEX idx_vp_vault_path  ON vault_promotions(vault_path);
CREATE INDEX idx_vp_created_at  ON vault_promotions(created_at DESC);

COMMENT ON TABLE vault_promotions IS
    'Record of Cooling Ledger entries promoted to Vault999 permanent memory.';


-- ─────────────────────────────────────────────────────────
-- TABLE 6: principal_override_budget
-- Override budget per principal per epoch.
-- Budget creates balance: unlimited override = human tyranny.
-- ─────────────────────────────────────────────────────────
CREATE TABLE principal_override_budget (
    principal_id      text        NOT NULL,
    epoch             text        NOT NULL,   -- e.g. '2026-06-28' or 'epoch-7'
    freezes_used      int         NOT NULL DEFAULT 0,
    reheats_used      int         NOT NULL DEFAULT 0,
    accelerates_used  int         NOT NULL DEFAULT 0,
    promotions_used   int         NOT NULL DEFAULT 0,
    budget_frees      int         NOT NULL DEFAULT 10,
    budget_reheats    int         NOT NULL DEFAULT 5,
    budget_accelerates int        NOT NULL DEFAULT 3,
    budget_promotions int         NOT NULL DEFAULT 2,
    updated_at        timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT pk_principal_override_budget
        PRIMARY KEY (principal_id, epoch)
);

COMMENT ON TABLE principal_override_budget IS
    'Override budget per principal per epoch. Enforces human-AI power balance.';


-- ─────────────────────────────────────────────────────────
-- HELPER FUNCTION: get_current_epoch
-- Returns current epoch string (date-based).
-- Override budgets are per-day to prevent abuse.
-- ─────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION cooling_ledger.get_current_epoch()
RETURNS text
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT to_char(now(), 'YYYY-MM-DD');
$$;


-- ─────────────────────────────────────────────────────────
-- HELPER FUNCTION: compute_decay_tier
-- Maps temperature to decay tier.
-- ─────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION cooling_ledger.compute_decay_tier(temp float8)
RETURNS text
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT CASE
        WHEN temp >= 0.75 THEN 'HOT'
        WHEN temp >= 0.50 THEN 'WARM'
        WHEN temp >= 0.25 THEN 'COOL'
        WHEN temp >  0.00 THEN 'FROZEN'
        ELSE                   'ERASED'
    END;
$$;


-- ─────────────────────────────────────────────────────────
-- HELPER FUNCTION: apply_decay
-- Applies temperature decay to a single entry.
-- Called by the metabolic decay job.
-- ─────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION cooling_ledger.apply_decay(
    p_entry_id    uuid,
    p_decay_rate  float8 DEFAULT 0.05,
    p_decay_reason text DEFAULT 'age'
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_old_temp   float8;
    v_new_temp   float8;
    v_old_tier   text;
    v_new_tier   text;
    v_triggered  text := 'kernel';
BEGIN
    -- Get current state
    SELECT temperature, decay_tier INTO v_old_temp, v_old_tier
    FROM cooling_ledger_entries
    WHERE id = p_entry_id AND deleted_at IS NULL
    FOR UPDATE;

    IF v_old_temp IS NULL THEN
        RETURN; -- entry gone or already deleted
    END IF;

    -- Compute new temperature (floor at 0)
    v_new_temp := greatest(0.0, v_old_temp - p_decay_rate);
    v_new_tier := cooling_ledger.compute_decay_tier(v_new_temp);

    -- Update entry
    UPDATE cooling_ledger_entries
    SET temperature = v_new_temp,
        decay_tier  = v_new_tier,
        updated_at  = now(),
        cooled_at   = CASE WHEN v_new_temp = 0 AND v_old_temp > 0 THEN now() ELSE cooled_at END
    WHERE id = p_entry_id;

    -- Log the decay event
    INSERT INTO cooling_decay_events
        (entry_id, old_temperature, new_temperature, old_tier, new_tier, decay_reason, triggered_by)
    VALUES
        (p_entry_id, v_old_temp, v_new_temp, v_old_tier, v_new_tier, p_decay_reason, v_triggered);
END;
$$;


-- ─────────────────────────────────────────────────────────
-- HELPER FUNCTION: apply_override
-- Principal overrides an entry: freeze, reheat, or accelerate.
-- Checks budget before executing.
-- ─────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION cooling_ledger.apply_override(
    p_entry_id      uuid,
    p_principal_id  text,
    p_action        text,   -- freeze | reheat | accelerate | void | promote
    p_justification text
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_entry         cooling_ledger_entries%ROWTYPE;
    v_epoch         text;
    v_budget_row    principal_override_budget%ROWTYPE;
    v_just_hash     text;
    v_new_temp      float8;
    v_new_tier      text;
    v_result        jsonb;
BEGIN
    -- Hash the justification for audit trail
    v_just_hash := encode(sha256(p_justification::bytea), 'hex');

    -- Get current epoch
    v_epoch := cooling_ledger.get_current_epoch();

    -- Get or create budget row
    BEGIN
        SELECT * INTO v_budget_row
        FROM principal_override_budget
        WHERE principal_id = p_principal_id AND epoch = v_epoch
        FOR UPDATE;

        IF NOT FOUND THEN
            INSERT INTO principal_override_budget (principal_id, epoch)
            VALUES (p_principal_id, v_epoch)
            ON CONFLICT (principal_id, epoch) DO NOTHING
            RETURNING * INTO v_budget_row;
        END IF;
    END;

    -- ── Budget enforcement ──
    IF p_action = 'freeze' THEN
        IF v_budget_row.freezes_used >= v_budget_row.budget_frees THEN
            RAISE EXCEPTION 'Override budget exceeded: freeze (%/%)',
                v_budget_row.freezes_used, v_budget_row.budget_frees
                USING ERRCODE = 'P0001';
        END IF;
    ELSIF p_action = 'reheat' THEN
        IF v_budget_row.reheats_used >= v_budget_row.budget_reheats THEN
            RAISE EXCEPTION 'Override budget exceeded: reheat (%/%)',
                v_budget_row.reheats_used, v_budget_row.budget_reheats
                USING ERRCODE = 'P0001';
        END IF;
    ELSIF p_action = 'accelerate' THEN
        IF v_budget_row.accelerates_used >= v_budget_row.budget_accelerates THEN
            RAISE EXCEPTION 'Override budget exceeded: accelerate (%/%)',
                v_budget_row.accelerates_used, v_budget_row.budget_accelerates
                USING ERRCODE = 'P0001';
        END IF;
    ELSIF p_action = 'promote' THEN
        IF v_budget_row.promotions_used >= v_budget_row.budget_promotions THEN
            RAISE EXCEPTION 'Override budget exceeded: promote (%/%)',
                v_budget_row.promotions_used, v_budget_row.budget_promotions
                USING ERRCODE = 'P0001';
        END IF;
    END IF;

    -- ── Get entry ──
    SELECT * INTO v_entry
    FROM cooling_ledger_entries
    WHERE id = p_entry_id AND deleted_at IS NULL
    FOR UPDATE;

    IF v_entry.id IS NULL THEN
        RAISE EXCEPTION 'Entry not found: %', p_entry_id USING ERRCODE = 'P0001';
    END IF;

    -- ── Apply action ──
    IF p_action = 'freeze' THEN
        -- Stop all decay, keep current temperature
        v_new_temp := v_entry.temperature;
        UPDATE cooling_ledger_entries
        SET temperature = v_new_temp, updated_at = now()
        WHERE id = p_entry_id;

        UPDATE principal_override_budget
        SET freezes_used = freezes_used + 1, updated_at = now()
        WHERE principal_id = p_principal_id AND epoch = v_epoch;

    ELSIF p_action = 'reheat' THEN
        -- Raise temperature back up
        v_new_temp := greatest(1.0, v_entry.temperature + 0.3);
        v_new_tier := cooling_ledger.compute_decay_tier(v_new_temp);
        UPDATE cooling_ledger_entries
        SET temperature = v_new_temp,
            decay_tier = v_new_tier,
            updated_at  = now(),
            cooled_at   = NULL
        WHERE id = p_entry_id;

        UPDATE principal_override_budget
        SET reheats_used = reheats_used + 1, updated_at = now()
        WHERE principal_id = p_principal_id AND epoch = v_epoch;

    ELSIF p_action = 'accelerate' THEN
        -- Force rapid decay
        v_new_temp := greatest(0.0, v_entry.temperature - 0.5);
        v_new_tier := cooling_ledger.compute_decay_tier(v_new_temp);
        UPDATE cooling_ledger_entries
        SET temperature = v_new_temp,
            decay_tier  = v_new_tier,
            updated_at   = now(),
            cooled_at    = CASE WHEN v_new_temp = 0 THEN now() ELSE cooled_at END
        WHERE id = p_entry_id;

        UPDATE principal_override_budget
        SET accelerates_used = accelerates_used + 1, updated_at = now()
        WHERE principal_id = p_principal_id AND epoch = v_epoch;

    ELSIF p_action = 'void' THEN
        UPDATE cooling_ledger_entries
        SET verdict_state = 'VOID',
            updated_at    = now()
        WHERE id = p_entry_id;

    ELSIF p_action = 'promote' THEN
        -- Mark as ready for vault promotion
        UPDATE cooling_ledger_entries
        SET verdict_state = 'SEAL_READY',
            updated_at    = now()
        WHERE id = p_entry_id;

        UPDATE principal_override_budget
        SET promotions_used = promotions_used + 1, updated_at = now()
        WHERE principal_id = p_principal_id AND epoch = v_epoch;
    END IF;

    -- Log the override
    INSERT INTO override_actions
        (entry_id, principal_id, action, justification_hash, justification_text)
    VALUES
        (p_entry_id, p_principal_id, p_action, v_just_hash, p_justification);

    -- Return result
    SELECT jsonb_build_object(
        'entry_id', p_entry_id,
        'action', p_action,
        'principal_id', p_principal_id,
        'justification_hash', v_just_hash,
        'budget_epoch', v_epoch
    ) INTO v_result;

    RETURN v_result;
END;
$$;


-- ─────────────────────────────────────────────────────────
-- HELPER FUNCTION: promote_to_vault
-- Promotes a SEAL_READY entry to Vault999.
-- The actual filesystem write happens outside Postgres.
-- This records the promotion metadata.
-- ─────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION cooling_ledger.promote_to_vault(
    p_entry_id      uuid,
    p_vault_path    text,
    p_seal_hash     text,
    p_promoted_by   text,
    p_reason        text DEFAULT NULL
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_result jsonb;
BEGIN
    INSERT INTO vault_promotions
        (entry_id, vault_path, seal_hash, promoted_by, promotion_reason)
    VALUES
        (p_entry_id, p_vault_path, p_seal_hash, p_promoted_by, p_reason)
    RETURNING jsonb_build_object(
        'id', id,
        'entry_id', entry_id,
        'vault_path', vault_path,
        'seal_hash', seal_hash,
        'created_at', created_at
    ) INTO v_result;

    -- Mark entry as sealed
    UPDATE cooling_ledger_entries
    SET verdict_state = 'SEALED',
        promoted_at   = now(),
        updated_at    = now()
    WHERE id = p_entry_id;

    RETURN v_result;
END;
$$;


-- ─────────────────────────────────────────────────────────
-- HELPER FUNCTION: check_budget
-- Returns current budget status for a principal.
-- ─────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION cooling_ledger.check_budget(
    p_principal_id text
)
RETURNS TABLE(
    epoch             text,
    freezes_used      int,
    reheats_used      int,
    accelerates_used  int,
    promotions_used   int,
    budget_frees      int,
    budget_reheats    int,
    budget_accelerates int,
    budget_promotions int
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT
        pb.epoch,
        pb.freezes_used,
        pb.reheats_used,
        pb.accelerates_used,
        pb.promotions_used,
        pb.budget_frees,
        pb.budget_reheats,
        pb.budget_accelerates,
        pb.budget_promotions
    FROM principal_override_budget pb
    WHERE pb.principal_id = p_principal_id
      AND pb.epoch = cooling_ledger.get_current_epoch();
END;
$$;


-- ─────────────────────────────────────────────────────────
-- HELPER FUNCTION: require_tri_witness
-- Enforces tri-witness for SEAL_READY entries.
-- Called by trigger before verdict_state can become SEAL_READY.
-- ─────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION cooling_ledger.require_tri_witness()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    IF NEW.verdict_state = 'SEAL_READY' AND OLD.verdict_state != 'SEAL_READY' THEN
        -- Check that we have all three witness types
        IF NOT EXISTS (
            SELECT 1 FROM witness_signatures ws
            WHERE ws.entry_id = NEW.id
            GROUP BY ws.entry_id
            HAVING
                bool_or(witness_type = 'human')   AND
                bool_or(witness_type = 'agent')   AND
                bool_or(witness_type = 'external')
        ) THEN
            RAISE EXCEPTION 'Tri-witness required before SEAL_READY: entry %', NEW.id
                USING ERRCODE = 'P0001';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;


-- ─────────────────────────────────────────────────────────
-- TRIGGER: tri_witness_guard
-- Fires before UPDATE on cooling_ledger_entries.
-- Prevents SEAL_READY without tri-witness.
-- ─────────────────────────────────────────────────────────
CREATE TRIGGER tri_witness_guard
    BEFORE UPDATE ON cooling_ledger_entries
    FOR EACH ROW
    EXECUTE FUNCTION cooling_ledger.require_tri_witness();


-- ─────────────────────────────────────────────────────────
-- TRIGGER: updated_at_auto
-- Auto-updates updated_at on every row change.
-- ─────────────────────────────────────────────────────────
CREATE TRIGGER tr_updated_at
    BEFORE UPDATE ON cooling_ledger_entries
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- Note: If handle_updated_at() doesn't exist, create it:
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'handle_updated_at') THEN
        CREATE OR REPLACE FUNCTION public.handle_updated_at()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN NEW.updated_at = now(); RETURN NEW; END; $$;
    END IF;
END;
$$;


-- ─────────────────────────────────────────────────────────
-- TRIGGER: log_decay_event
-- Auto-logs temperature changes to cooling_decay_events.
-- ─────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION cooling_ledger.log_temperature_change()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    IF NEW.temperature != OLD.temperature THEN
        INSERT INTO cooling_decay_events
            (entry_id, old_temperature, new_temperature,
             old_tier, new_tier, decay_reason, triggered_by)
        VALUES
            (NEW.id, OLD.temperature, NEW.temperature,
             OLD.decay_tier, NEW.decay_tier, 'manual', 'kernel');
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_log_temperature_change
    AFTER UPDATE ON cooling_ledger_entries
    FOR EACH ROW
    WHEN (NEW.temperature IS DISTINCT FROM OLD.temperature)
    EXECUTE FUNCTION cooling_ledger.log_temperature_change();


-- ─────────────────────────────────────────────────────────
-- TRIGGER: budget_epoch_default
-- Auto-creates budget row for new principals.
-- ─────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION cooling_ledger.ensure_budget_row()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO principal_override_budget (principal_id, epoch)
    VALUES (NEW.principal_id, cooling_ledger.get_current_epoch())
    ON CONFLICT (principal_id, epoch) DO NOTHING;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_ensure_budget_row
    AFTER INSERT ON cooling_ledger_entries
    FOR EACH ROW
    WHEN (NEW.principal_id IS NOT NULL)
    EXECUTE FUNCTION cooling_ledger.ensure_budget_row();


-- ─────────────────────────────────────────────────────────
-- RLS POLICIES
-- Kernel-only write. Read is governed.
-- ─────────────────────────────────────────────────────────
ALTER TABLE cooling_ledger_entries     ENABLE ROW LEVEL SECURITY;
ALTER TABLE cooling_decay_events       ENABLE ROW LEVEL SECURITY;
ALTER TABLE witness_signatures         ENABLE ROW LEVEL SECURITY;
ALTER TABLE override_actions           ENABLE ROW LEVEL SECURITY;
ALTER TABLE vault_promotions           ENABLE ROW LEVEL SECURITY;
ALTER TABLE principal_override_budget  ENABLE ROW LEVEL SECURITY;

-- Kernel service role: full access
CREATE POLICY kernel_full_access_entries
    ON cooling_ledger_entries FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY kernel_full_access_decay
    ON cooling_decay_events FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY kernel_full_access_witness
    ON witness_signatures FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY kernel_full_access_override
    ON override_actions FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY kernel_full_access_promotion
    ON vault_promotions FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY kernel_full_access_budget
    ON principal_override_budget FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Authenticated read (for audit/gateway)
CREATE POLICY authenticated_read_entries
    ON cooling_ledger_entries FOR SELECT
    TO authenticated
    USING (deleted_at IS NULL);

CREATE POLICY authenticated_read_decay
    ON cooling_decay_events FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY authenticated_read_witness
    ON witness_signatures FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY authenticated_read_override
    ON override_actions FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY authenticated_read_promotion
    ON vault_promotions FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY authenticated_read_budget
    ON principal_override_budget FOR SELECT
    TO authenticated
    USING (true);


-- ─────────────────────────────────────────────────────────
-- GRANT
-- ─────────────────────────────────────────────────────────
GRANT USAGE ON SCHEMA cooling_ledger TO service_role, authenticated;
GRANT ALL ON cooling_ledger_entries      TO service_role;
GRANT SELECT ON cooling_ledger_entries    TO authenticated;
GRANT ALL ON cooling_decay_events         TO service_role;
GRANT SELECT ON cooling_decay_events      TO authenticated;
GRANT ALL ON witness_signatures           TO service_role;
GRANT SELECT ON witness_signatures        TO authenticated;
GRANT ALL ON override_actions             TO service_role;
GRANT SELECT ON override_actions          TO authenticated;
GRANT ALL ON vault_promotions             TO service_role;
GRANT SELECT ON vault_promotions          TO authenticated;
GRANT ALL ON principal_override_budget     TO service_role;
GRANT SELECT ON principal_override_budget   TO authenticated;
GRANT ALL ON SCHEMA cooling_ledger         TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA cooling_ledger TO service_role;


-- ─────────────────────────────────────────────────────────
-- METADATA
-- ─────────────────────────────────────────────────────────
COMMENT ON SCHEMA cooling_ledger IS
    'AI governed short-term memory. Cooling Ledger = Postgres, Vault999 = filesystem JSONL.';
