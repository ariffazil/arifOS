# CANON.md — Canonical Architecture Map (AGI_ASI_bot)

This file declares **which files are canonical** at each layer of your stack and how conflicts are resolved.
It is the authoritative map for:
- Runtime OpenClaw workspace (live behavior)
- AGI_ASI_bot client spec (this repo)
- oo0-STATE constitutional state bus (governance + state)

If any other document contradicts this map, **CANON.md wins**.

---

## Layer 1 — Runtime (Live OpenClaw Workspace)

**Path:** `~/.openclaw/workspace/`

These files define **live execution behavior** for the running OpenClaw instance:

- `AGENTS.md`        — instructions / behavior
- `SOUL.md`          — persona / tone
- `USER.md`          — user preferences
- `IDENTITY.md`      — runtime view of system identity
- `MEMORY.md`        — long-term summary
- `memory/YYYY-MM-DD` — daily logs
- `HEARTBEAT.md`     — ops checklist / health
- `BOOTSTRAP.md`     — startup checklist

At runtime, OpenClaw reads these first. They must eventually be kept in sync with the higher layers below.

---

## Layer 2 — Client Spec (AGI_ASI_bot)

**Path:** `/root/AGI_ASI_bot/`

These files define the **governed OpenClaw personality and behavior contracts**.

### Primary Canon (Client Level)

These override runtime workspace intent when there is a mismatch:

- `AGENTS.md`       — agent roles, behavior rules, DSUP, Non-regression
- `ARCHITECTURE.md` — Trinity + stack architecture (OpenClaw, oo0-STATE, arifOS)
- `DIRECTIVE.md`    — high-level system directives / operating mode

### Secondary (UX / Tooling Spec)

These describe tools, UX, and formatting but are subordinate to Primary Canon:

- `TRINITY.md`         — conceptual Trinity framing (Δ · Ω · Ψ)
- `TOOLS.md`           — tool descriptions and semantics
- `AGI_TOOLSTACK.md`   — full stack/tooling overview
- `TELEGRAM_FORMAT.md` — formatting + UX rules for Telegram

### Legacy / Reference

These are **historical contracts** kept for reference; they do not override Primary Canon:

- `AGI_CORE_CONTRACT_v1.0.md`

---

## Layer 3 — Constitutional State Bus (oo0-STATE)

**Path:** `/root/oo0-STATE/state/`

This layer defines the **constitutional state bus and governance**. It is the ultimate source of truth for state layout and floor enforcement.

### Contracts (Constitutional Canon)

- `state/contracts/shared/AGENTS.md`   — canonical agent roles + DSUP for all runtimes
- `state/contracts/shared/RULES.md`    — global governance rules (FAST vs GOVERNED, FREEZE, etc.)
- `state/contracts/shared/IDENTITY.yaml` — system identity, owner, mode
- `state/contracts/shared/schemas/`    — JSON Schemas for logs, configs, state

### Runtime Spine

- `state/runtime/openclaw/workspace/`  — OpenClaw workspace under the bus
- `state/runtime/opencode/`            — OpenCode state (logs, checkpoints, runs, agents)
- `state/runtime/agentzero/`           — AgentZero state (pipelines, docker metadata, logs)

### Governance

- `state/governance/ledger/`   — append-only audit ledger (JSONL)
- `state/governance/verdicts/` — floor verdicts per subsystem
- `state/governance/vault/`    — VAULT-999 sealed records
- `state/governance/constitutional/` — floor definitions and related docs

---

## Canon Rules (Conflict Resolution)

1. **oo0-STATE is the constitutional source of truth.**  
   - If there is a conflict about state layout, governance rules, or floor semantics, the oo0-STATE contracts win.

2. **AGI_ASI_bot is the client behavioral contract.**  
   - It describes how the governed OpenClaw personality should behave on top of oo0-STATE.  
   - If AGI_ASI_bot/AGENTS.md conflicts with the runtime workspace AGENTS.md, AGI_ASI_bot wins (after migration is complete).

3. **Runtime workspace reflects the active execution layer.**  
   - It can drift temporarily during development, but the goal is for workspace files to be a **view** of oo0-STATE + AGI_ASI_bot, not an independent canon.

4. **Conflict precedence (long-term target):**  
   - `oo0-STATE` **>** `AGI_ASI_bot` **>** `~/.openclaw/workspace`.

5. **Migration note:**  
   - Older documentation and scripts may treat `sovereign_data/workspace` or `~/.openclaw/workspace` as the canonical bus.  
   - **Future versions** will relocate the canonical workspace under `oo0-STATE/state/runtime/openclaw/workspace/` and treat `~/.openclaw/workspace` as a mounted view or compatibility lane.

---

## DSUP and Governance

- DSUP (Dual Status Update Protocol) is the **mandatory format** for status/progress reporting across this stack.  
- Full 13-LAW enforcement requires arifOS / aaa-mcp; when arifOS is unavailable, the system operates in **degraded advisory mode**.

CANON.md does not redefine DSUP or floors; it declares **where those definitions live** and which files override which when there is a disagreement.
