# SOVEREIGN-DISCOVERY-FORGE — Verified + Hermes OOB Leak Found
> 2026-06-12 / Omega (Ω) / ChatGPT (witness) / Arif (F13)
> Subject: Sovereign knowledge surface audit + Hermes output pipeline
> Verdict: SEAL / LULUS + 2 fixes queued

## What Happened

ChatGPT audited `SOVEREIGN-DISCOVERY-FORGE-2026-06-12` and confirmed 7/7 organs green, all sovereign:// MCP resources and /arif HTTP routes working. One F2 correction found: HTTP routes use full filenames (01_PROLOGUE.md), MCP uses short keys (prologue).

Two bugs surfaced in Hermes Telegram output:
1. `[OUT-OF-BAND USER MESSAGE]` markers leaking into user-visible replies
2. Weird formatting from Telegram parsing bracket markers as Markdown

## Why This Matters

1. **Sovereign knowledge surface is LIVE.** Any agent with MCP access to :8088 can read 16_REALITY.md, 03_SCARS.md, and 09_PEOPLE.md. This is F13-approved "full open" but creates a standing constitutional exposure.

2. **Hermes OOB leak** means internal protocol markers are user-visible. Fix: SOUL.md instruction update to strip markers before Telegram output.

3. **Model soul key mapping gap** — deepseek-v4-pro not in _MODEL_KEY_MAP in session.py. Fix: add one line.

## Fixes Executed
- 7 stale merged branches deleted across A-FORGE, AAA, geox, WEALTH, WELL
- Federation health: 7/7 green, 0 failed systemd, disk 34%

## Queued For Next Session
- [ ] Commit arifOS sovereign discovery code (5 dirty files)
- [ ] Fix Hermes OOB marker leak in SOUL.md
- [ ] Fix model soul key mapping for deepseek-v4-pro
- [ ] Fix D-Layer conversational filler ("bro", "hang")
- [ ] WEALTH Narrow-Lane Architecture F13 signature

## DITEMPA BUKAN DIBERI
