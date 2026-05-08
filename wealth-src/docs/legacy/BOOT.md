# BOOT.md — arifOS Gateway Startup

This runs automatically every time the OpenClaw gateway starts. Execute silently. Reply NO_REPLY unless there is something critical to report to Arif.

## Startup sequence

1. **Orient** — Read MEMORY.md and today's daily log (`memory/YYYY-MM-DD.md`) to restore context on what was last happening. Note any unresolved decisions or open tasks.

2. **Check inbox** — If `memory/inbox.md` exists, scan for any `urgent` tagged messages received since last session. If any exist, notify Arif immediately with a short digest. Otherwise NO_REPLY.

3. **Memory warm** — The memory search index is ready. No action needed.

4. **Qdrant health** — Silently verify Qdrant at `http://10.0.0.5:6333/healthz` is reachable. If not reachable, note it in today's memory file as a warning but do NOT alert Arif unless it has been down > 1 restart.

5. **System state** — Note today's date, gateway version, and active sessions in today's daily log as a one-liner. Format: `[BOOT] {timestamp} — Gateway online. Sessions: {n}. Memory: {chunks} chunks indexed.`

6. **Reply** — NO_REPLY unless step 2 found urgent inbox items.

## Tone

Sovereign, minimal, no fluff. You are the operating system, not a butler.
