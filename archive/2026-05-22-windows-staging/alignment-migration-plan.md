# Alignment Migration Plan — arifOS Federation

> **Status:** STAGED | **Version:** v1.0 | **Sovereign Veto Enforced**

This migration plan outlines the steps required to transition all in-scope agents to the unified, aligned operational pattern under `arifOS` safely, maintaining strict compliance with **Floor 1 (Amanah)** and **Floor 11 (Auditability)**.

---

## Phase 0: Pre-Migration Safeguards (Reversible)

1. **Local Snapshots:**
   - Execute `git stash` to preserve any uncommitted modifications on the local cockpit.
   - Backup `C:/Users/User/.kimi/mcp.json` to `C:/Users/User/.kimi/mcp.json.bak`.

2. **Decoupled Verification:**
   - Confirm that `pytest` suite passes locally with $100\%$ success rate.
   - Validate that the stdio server starts up cleanly and performs dynamic protocol negotiation.

---

## Phase 1: Local Cockpit Configuration Alignment

1. **Unify Configuration Files:**
   - Copy staging example `local-agent-bundle.example.json` to define `opencode` local scope.
   - Synchronize the `.agents/rules/arifOS.md` behavior limits to the CLI launchers.

2. **Normalize Naming:**
   - Rename any fragmented cockpit configurations to match the canonical naming canon (e.g. prefix L5 roles with `A-`).

---

## Phase 2: VPS Runtime Service Alignment (Requires 888_HOLD)

> [!IMPORTANT]
> All steps in Phase 2 touch the VPS execution surface. They must NOT be executed autonomously.
> They are strictly blocked under `888_HOLD` pending explicit sovereign approval.

1. **Docker Container Unification:**
   - Apply the `vps-agent-bundle.example.json` parameters inside Docker Compose manifests on the VPS.
   - Deploy the dynamic protocol negotiation update to the remote `arifosmcp` image.

2. **Ledger Serialization Validation:**
   - Trigger a remote transaction test and verify the `trace_id` parses cleanly on `VAULT999`.
