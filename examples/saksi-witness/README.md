# SAKSI — The arifOS Witness Pattern (Reference App)

> **"Never let the agent that writes the code be the agent that declares the server healthy. Put a thin, read-only Witness in front of raw logs, and lock every mutation behind an HMAC human switch."**
>
> **Pattern Class:** Reference MCP Client & Runtime Governance Surface  
> **Constitutional Principle:** `Author ≠ Judge` (F2 Truth · F3 Tri-Witness · F11 Auditability · F13 Sovereign)  
> **Full Architectural Blueprint:** [`../../docs/patterns/saksi-witness.md`](../../docs/patterns/saksi-witness.md)

---

## 1. The 30-Second Problem: Narrative Bias vs. Raw Observability

When autonomous coding agents and full-loop executive agents share a production host, **they grade their own homework**.

A coding agent patches a file on disk, verifies its unit tests, and declares `100% VERIFIED`. An executive agent reads the receipt and celebrates. Meanwhile, in RAM:
- The running systemd process has not loaded the disk patch (`disk ≠ RAM` drift).
- `journalctl` is quietly bleeding retry loops (`Text must be non-empty`) or rejecting peer traffic.
- Agents talking to each other in a shared chat channel trigger rate-limit cooldowns.

Adding *another* heavy multi-agent loop does not fix this—it creates a four-agent echo chamber with the same blind spots.

**SAKSI** (*"Witness of Agentic REALITY by arifOS"*) solves this through **Asymmetric Role Separation**:
1. **1-Shot Read-Only Watchdog:** A ~400-line Python script with **no autonomous multi-turn loop** and **no code-writing tools**. Because it cannot write code, it has zero conflict of interest when reading `journalctl`.
2. **Direct MCP Consumer:** Reads raw kernel posture (`arif_init` in `OBSERVE_ONLY`, `arif_observe` / `kernel_health`, `fq_pulse`, `arif_route`) and raw systemd/journal telemetry (`ops_diagnose`).
3. **888 HMAC Circuit-Breaker:** Its only mutation path is a single-use, time-bounded (10-minute TTL) cryptographic HMAC inline button (`[✅ Restart] [❌ Cancel]`) that only the human sovereign (`F13`) can press—and only when `systemctl is-failed` is true and rate-limit gates (`1/30m`, `3/24h`) pass.

---

## 2. Tri-Witness Architecture (Asymmetric Role Separation)

```text
  ┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
  │   Builder (333-AGI)     │     │   Executive (HERMES)    │     │  Edge Scout (OpenClaw)  │
  │  Writes code & tests    │     │  Full agentic loop      │     │  Remote recon & ingest  │
  │  Commits to git         │     │  Multi-MCP orchestration│     │  Pushes JSON via A2A    │
  └────────────┬────────────┘     └────────────┬────────────┘     └────────────┬────────────┘
               │                               │                               │
               └───────────────────────────────┼───────────────────────────────┘
                                               │
                     (Agents CANNOT certify their own runtime health: Author ≠ Judge)
                                               │
                                               ▼
                 ┌───────────────────────────────────────────────────────────┐
                 │         SAKSI — 1-Shot Read-Only Runtime Witness          │
                 │  • Binds arifOS Kernel (:8088/mcp) in OBSERVE_ONLY mode   │
                 │  • Probes raw journalctl & systemd (:7072/mcp)            │
                 │  • Rejects "all clear" prose if raw error counts > 0      │
                 └─────────────────────────────┬─────────────────────────────┘
                                               │
                            If unit is failed & passes 1/30m + 3/24h gates:
                            Emits single-use HMAC-SHA256 token (TTL 10m)
                                               │
                                               ▼
                 ┌───────────────────────────────────────────────────────────┐
                 │        Human Sovereign (F13 / 888 Circuit-Breaker)        │
                 │        Presses [✅ Restart] or [❌ Cancel] on Telegram     │
                 └─────────────────────────────┬─────────────────────────────┘
                                               │
                                               ▼
                 ┌───────────────────────────────────────────────────────────┐
                 │      A-FORGE (:7072/mcp) → Lease-Bound Execution          │
                 │      Followed 5 min later by SAKSI Post-Deploy SEAL Probe │
                 └───────────────────────────────────────────────────────────┘
```

| Role | Archetype | Loop Depth | Authority Ceiling | Why the Boundary Exists |
|---|---|---|---|---|
| **Builder** (`333-AGI`) | Coding Agent | Multi-turn CLI / IDE | `PROPOSE / MUTATE_CODE` | Optimizes for passing tests on disk; blind to post-deploy runtime drift. |
| **Executive** (`HERMES`) | Meaning & Orchestration | Full autonomous loop | `ROUTE / ORCHESTRATE` | Carries deep conversational context; prone to narrative optimism. |
| **Scout** (`OpenClaw`) | Edge Recon Node | Event-driven / cron | `INGEST / A2A_PUSH` | Isolated on an edge host; pushes structured JSON to A2A, never self-approves. |
| **Witness** (`SAKSI`) | **1-Shot Watchdog** | **1-Shot (No Loop)** | **`OBSERVE_ONLY` + `888_HMAC_PROPOSE`** | **Cannot write code, so it never defends broken code. Counts raw log lines.** |

---

## 3. Files in This Reference Package

| File | Purpose |
|---|---|
| [`README.md`](./README.md) | Architectural overview, Tri-Witness role separation, and Post-Deploy SEAL protocol. |
| [`SOUL.template.md`](./SOUL.template.md) | The prompt contract that enforces `OBSERVE_ONLY` epistemic discipline and bans constitutional jargon from human output. Reloaded dynamically per turn so persona updates never require a service restart. |
| [`saksi_reference.py`](./saksi_reference.py) | Sanitized, self-contained Python reference implementation of the 1-shot MCP client + HMAC-SHA256 inline-button circuit-breaker. |

---

## 4. Quickstart (Run Your Own SAKSI Witness)

```bash
pip install httpx fastapi uvicorn

export WITNESS_BOT_TOKEN="123456789:AAExampleTelegramBotToken"
export OWNER_TELEGRAM_ID="100000001"
export WITNESS_HMAC_SECRET="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
export KERNEL_MCP_URL="http://127.0.0.1:8088/mcp"
export FORGE_MCP_URL="http://127.0.0.1:7072/mcp"
export LLM_CHAT_URL="http://127.0.0.1:4000/v1/chat/completions"

python examples/saksi-witness/saksi_reference.py
```

---

## 5. The Post-Deploy SEAL Protocol (5-Minute Verification Gate)

Under the **arifOS Witness Pattern**, no service patch or deployment is marked `SEALED / COMPLETED` when the builder finishes editing files. Closure requires an independent **SAKSI SEAL Probe** against the running `MainPID` / `_SYSTEMD_INVOCATION_ID`:

1. **Disk vs. RAM Proof:** Verify `stat -c '%Y' <patched_file>` is strictly older than `systemctl show -p ActiveEnterTimestamp <unit>`. If `mtime > ActiveEnterTimestamp`, the patch is staged on disk, **not** active in RAM.
2. **Invocation-Scoped Log Count:** Filter `journalctl` by `_SYSTEMD_INVOCATION_ID` (never by a rough wall-clock window that mixes pre-restart and post-restart logs).
3. **Zero-Regression Gate:**
   - `PARKED_MCP_CNT == 0` (no MCP servers failed to bind at startup)
   - `EMPTY_TEXT_CNT == 0` (no empty-payload outbound retries)
   - `SINGLE_POLLER == PASS` (no duplicate processes polling the same bot credential)

Only when **SAKSI** independently witnesses `0` regressions on the live invocation ID does the session close.

**Ditempa Bukan Diberi** — *Forged, Not Given.*
