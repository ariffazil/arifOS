# The arifOS Witness Pattern — SAKSI Reference Architecture

> **Status:** Production-Verified Reference Pattern (2026-11-22)  
> **Reference Implementation:** [`examples/saksi-witness/`](../../examples/saksi-witness/)  
> **Constitutional Floors Exercised:** `F1` (Amanah) · `F2` (Truth) · `F3` (Tri-Witness) · `F8` (Genius / Least Power) · `F11` (Auditability) · `F13` (Sovereign Veto)

---

## 1. Why Autonomous Agents Cannot Audit Their Own Health

Most multi-agent stacks fail in production not because their models are weak, but because **their verification loop shares the same cognitive substrate as their execution loop**.

When a coding agent (`Builder`) and an orchestrator agent (`Executive`) run on the same host:
1. **Narrative Contamination:** Once an agent emits a receipt claiming a fix is complete, peer agents reading that receipt inherit the conclusion instead of re-probing the raw operating system.
2. **Disk vs. RAM Blindness (`mtime > ActiveEnterTimestamp`):** Coding agents verify files on disk (`git diff`, `pytest`). They routinely forget that a long-running daemon (`MainPID`) is still executing the old bytecode in RAM until restarted—or conversely, that an `OnFailure` systemd trigger already loaded the patch minutes ago.
3. **Bot-to-Bot Echo Chambers:** Putting multiple autonomous full-loop bots in the same chat room turns a human command surface into an unthrottled message bus, triggering rate-limit cooldowns and `Unauthorized` log storms.

The arifOS solution is **SAKSI** (*"Witness of Agentic REALITY by arifOS"*): a deliberately thin, **1-shot, read-only runtime witness** paired with an **888 HMAC human circuit-breaker**.

---

## 2. The Four Laws of the Witness Pattern

### Law 1 — Capability Restriction Is Constitutional Power (`Author ≠ Judge`)
SAKSI has **no multi-turn agentic loop**, **no file-writing tools**, and **no shell mutation authority**. Every session it opens with the arifOS kernel (`:8088/mcp`) is bound at `requested_authority="OBSERVE_ONLY"`. Because it cannot author code, it never defends broken code.

### Law 2 — Raw Telemetry Outranks Agent Receipts (`F2 Truth`)
SAKSI does not read peer agents' markdown summaries to decide if a service is healthy. It calls `ops_diagnose` (`systemctl show` + `journalctl -n 40`), `kernel_health` (`:8088/health`), and `fq_pulse` (`:7073/health`), reporting raw line counts and episode counts.

### Law 3 — Chat Is a Human UI, Never an Agent Message Bus (`F8 Least Power`)
Inter-agent coordination travels over structured machine transports (NATS JetStream, A2A JSON-RPC envelopes, arifFlow receipts). Telegram is reserved strictly for:
- Human-to-agent intent and status readouts.
- The **888 HMAC Circuit-Breaker** inline approval buttons (`[✅ Restart] [❌ Cancel]`).

### Law 4 — Two-Gate Cryptographic Human Switch (`F1 Amanah` + `F13 Sovereign`)
When a service fails, SAKSI cannot restart it autonomously. Even proposing a restart button requires passing two deterministic gates in Python (`llm_consulted: false`):
- **Gate 1 (`is-failed`):** The target unit must be in ` ALLOWLIST_UNITS` and genuinely failing (`systemctl is-failed`), preventing hallucinated restarts of healthy services.
- **Gate 2 (Rate-Limit Envelope):** Maximum **1 restart per 30 minutes** and **3 restarts per 24 hours** per unit. If a service crashes 3 times in a day, restarting is blocked and escalated to an architectural `888_HOLD`.
- **Single-Use HMAC-SHA256 Token:** The `[✅ Restart]` callback carries an HMAC signature over `unit | chat_id | owner_id | expiry_10m | nonce`. Replay, expiry, or clicks from any user other than the sovereign (`F13`) fail closed.

---

## 3. Production Incident Record (2026-11-22 — Two-Pass Witness Verification)

The table below documents an actual production incident where the Tri-Witness architecture caught live defects across two passes and refused premature closure (`Author ≠ Judge`) until every signal in `journalctl` was accounted for:

| Phase | Actor | Action & Observation |
|---|---|---|
| **1. Initial Build & Claim** | `333-AGI` (Builder) | Repaired a broken Python virtualenv (`fastapi` + `opentelemetry-api`) for the executive gateway service, closed its session receipt, and declared the repair verified. |
| **2. Witness Pass #1** | **`SAKSI`** (1-Shot Witness) | Ignored the builder's receipt and probed `journalctl` directly. Caught **3 live defects** still bleeding in production: (a) 24 lines (5 retry episodes) of Telegram `400 Bad Request: Text must be non-empty`, (b) ~30 `Unauthorized` drops when the edge scout (`OpenClaw`) spoke in a shared group, and (c) `BotLoopGuard` cooldowns. |
| **3. Source Repair #1** | `333-AGI` (Builder) | Patched empty-chunk filtering + `retryable=False` in the Telegram adapter, and separated `BotLoopGuard` cooldown logs (`INFO`) from stranger DM blocks (`WARNING`). |
| **4. Witness Pass #2 (SEAL Refusal)** | **`SAKSI`** + `OpenClaw` | Even after post-restart `Text must be non-empty` and group `Unauthorized` counts dropped to `0`, **SAKSI refused to stamp `SEAL COMPLETED`** and held GitHub publication because 3 signals remained visible in the boot window: (1) `T5b single-poller: OBSERVATION_FAILED` (`cannot read MainPID` during `ExecStartPre` when `MainPID=0` while a status dashboard held sockets), (2) `HALT_NO_DELIVERY` on startup notification (`home_channel.chat_id` was set to the bot's own ID instead of `home_channel.user_id`), and (3) 4 `Blocked unauthorized user` entries (proven by `OpenClaw` and `channel_directory.json` to be an external DM user spoofing the display name `"BotFather"`, rightly blocked by the DM allowlist). |
| **5. Source Repair #2** | `333-AGI` (Builder) | Fixed `poller-uniqueness.py` so pre-start `MainPID=0` with only non-gateway status surfaces passes (`6/6` unit tests `ALL-GREEN`, `T5b single-poller: PASS`), and fixed `home_channel` bot-ID -> human `user_id` resolution in `config.yaml` and `run_notifications.py`. |

---

## 4. Reference Code & Templates

- **Runnable Reference Client:** [`examples/saksi-witness/saksi_reference.py`](../../examples/saksi-witness/saksi_reference.py)
- **Witness Persona Contract:** [`examples/saksi-witness/SOUL.template.md`](../../examples/saksi-witness/SOUL.template.md)
- **Quickstart & SEAL Checklist:** [`examples/saksi-witness/README.md`](../../examples/saksi-witness/README.md)
