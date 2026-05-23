-- arifos_plan — Postgres Schema v1.0
-- Planning Organ persistence layer
-- DITEMPA BUKAN DIBERI — Forged, Not Given

BEGIN;

-- ─── sovereign_intents ──────────────────────────────────────────────────────
CREATE TABLE sovereign_intents (
    intent_id    VARCHAR(64) PRIMARY KEY,
    description  TEXT NOT NULL,
    constraints   JSONB DEFAULT '{}',
    floors        JSONB DEFAULT '{}',
    risk_prelude  JSONB DEFAULT '{}',
    created_by    VARCHAR(128) NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    status        VARCHAR(32) DEFAULT 'ACTIVE'
);

-- ─── plans ───────────────────────────────────────────────────────────────────
CREATE TABLE plans (
    plan_id          VARCHAR(64) PRIMARY KEY,
    intent_id        VARCHAR(64) REFERENCES sovereign_intents(intent_id),
    epoch_id         VARCHAR(128),
    status           VARCHAR(32) NOT NULL DEFAULT 'DRAFT',
                        -- DRAFT | PENDING_APPROVAL | APPROVED | IN_EXECUTION
                        -- COMPLETED | ABORTED | FAILED
    risk_band        VARCHAR(16) NOT NULL DEFAULT 'MEDIUM',
                        -- LOW | MEDIUM | HIGH | CRITICAL
    irreversible     BOOLEAN NOT NULL DEFAULT FALSE,
    hold_reason      TEXT,
    analysis         JSONB DEFAULT '{}',
                        -- {floors_checked, irreversibility_summary, holds}
    metadata         JSONB DEFAULT '{}',
    created_by       VARCHAR(128) NOT NULL,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);

-- ─── plan_tasks ─────────────────────────────────────────────────────────────
CREATE TABLE plan_tasks (
    task_id                 VARCHAR(64) PRIMARY KEY,
    plan_id                 VARCHAR(64) REFERENCES plans(plan_id) ON DELETE CASCADE,
    description             TEXT NOT NULL,
    tool                    VARCHAR(128) NOT NULL,
    mutates_external_state  BOOLEAN NOT NULL DEFAULT TRUE,
    target_surface          VARCHAR(256),
    reversible              BOOLEAN NOT NULL DEFAULT FALSE,
    risk_band               VARCHAR(16) NOT NULL DEFAULT 'LOW',
    status                  VARCHAR(32) NOT NULL DEFAULT 'PLANNED',
                        -- PLANNED | RUNNING | COMPLETED | FAILED | SKIPPED
    dependencies            TEXT[] DEFAULT '{}',
    result                  JSONB,
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    completed_at            TIMESTAMPTZ
);

-- ─── plan_receipts ──────────────────────────────────────────────────────────
CREATE TABLE plan_receipts (
    receipt_id      VARCHAR(64) PRIMARY KEY,
    plan_id         VARCHAR(64) REFERENCES plans(plan_id) ON DELETE CASCADE,
    decision        VARCHAR(16) NOT NULL,
                        -- APPROVED | REJECTED | HOLD | MODIFIED
    decided_by      VARCHAR(128) NOT NULL,
    decided_at      TIMESTAMPTZ DEFAULT NOW(),
    notes           TEXT DEFAULT '',
    floor_signatures JSONB DEFAULT '[]'
);

-- ─── execution_receipts ──────────────────────────────────────────────────────
CREATE TABLE execution_receipts (
    receipt_id    VARCHAR(64) PRIMARY KEY,
    epoch_id       VARCHAR(128),
    plan_id        VARCHAR(64) REFERENCES plans(plan_id) ON DELETE CASCADE,
    task_id        VARCHAR(64) REFERENCES plan_tasks(task_id) ON DELETE CASCADE,
    status         VARCHAR(32) NOT NULL,
                        -- COMPLETED | FAILED | SKIPPED
    started_at     TIMESTAMPTZ,
    finished_at    TIMESTAMPTZ,
    logs_ref       TEXT,
    error          TEXT,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Indexes ────────────────────────────────────────────────────────────────
CREATE INDEX idx_plans_status     ON plans(status);
CREATE INDEX idx_plans_epoch      ON plans(epoch_id);
CREATE INDEX idx_tasks_plan       ON plan_tasks(plan_id);
CREATE INDEX idx_tasks_status     ON plan_tasks(status);
CREATE INDEX idx_receipts_plan    ON plan_receipts(plan_id);
CREATE INDEX idx_exec_plan        ON execution_receipts(plan_id);

-- ─── GK runtime check ───────────────────────────────────────────────────────
-- Governance Kernel check: plan is APPROVED and no unresolved 888_HOLD
CREATE OR REPLACE FUNCTIONgk_can_execute(p_plan_id VARCHAR, p_task_id VARCHAR)
RETURNS JSONB AS $$
DECLARE
    v_plan   JSONB;
    v_task   JSONB;
    v_receipt JSONB;
BEGIN
    SELECT to_jsonb(p.*) INTO v_plan FROM plans p WHERE plan_id = p_plan_id;
    IF NOT FOUND OR v_plan->>'status' != 'APPROVED' THEN
        RETURN jsonb_build_object('can_execute', false, 'reason', 'Plan not APPROVED');
    END IF;

    SELECT to_jsonb(t.*) INTO v_task FROM plan_tasks t WHERE task_id = p_task_id AND plan_id = p_plan_id;
    IF NOT FOUND THEN
        RETURN jsonb_build_object('can_execute', false, 'reason', 'Task not found in plan');
    END IF;

    -- Check for unresolved 888_HOLD on this task
    IF v_task->>'risk_band' IN ('HIGH','CRITICAL') OR (v_task->>'reversible')::boolean = false THEN
        -- Check no APPROVED receipt that bypasses hold
        SELECT to_jsonb(r.*) INTO v_receipt FROM plan_receipts r
        WHERE plan_id = p_plan_id AND decision = 'APPROVED'
        ORDER BY decided_at DESC LIMIT 1;
        IF v_receipt IS NULL THEN
            RETURN jsonb_build_object(
                'can_execute', false,
                'reason', '888_HOLD: task requires sovereign approval',
                'task_id', p_task_id
            );
        END IF;
    END IF;

    RETURN jsonb_build_object('can_execute', true, 'plan_id', p_plan_id, 'task_id', p_task_id);
END;
$$ LANGUAGE plpgsql;

COMMIT;
