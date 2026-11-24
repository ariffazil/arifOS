---
name: arif-a2a-call
description: A2A v1.0.0 client + 888 JUDGMENT integration for OPENCLAW. Use when candidate actions require ASI deliberation or A2A federation with APEX (formerly Hermes).
version: 2026.05.01
tags: [a2a, federation, judgment, apex, 888]
---

# arif-a2a-call — A2A Client for OPENCLAW

Use this skill when OPENCLAW needs 888 JUDGMENT or constitutional deliberation.

## Architecture

```
OPENCLAW
  └── MCP ──── arifOS MCP ──── arif_judge_deliberate (888 JUDGMENT)
```

## Judgment Path

### Primary 888 — arifOS MCP (arif_judge_deliberate) [ACTIVE]

Use the arifOS MCP tool `arif_judge_deliberate` for constitutional judgment:

```
Tool: arif_judge_deliberate
  mode: judge
  candidate: <action text>
  session_id: <current session>
  actor_id: openclaw
```

Returns: SEAL / HOLD / VOID with floor compliance proof.

### A2A Fallback — APEX / AAA Gateway [DISABLED]

> [!WARNING]
> **STATUS: DISABLED (2026-11-24 · F13 Audit)**
> Laluan terus A2A fallback (port 3001/3002) dinyahaktifkan kerana token dev lama telah dibatalkan dan belum diprovsyenkan semula.
> Kredensial tidak didaftarkan dalam runtime env; sebarang cubaan memanggil endpoint A2A akan gagal.
> **Satu-satunya laluan sah dan aktif ialah Step 1: arifOS MCP (`arif_judge_deliberate`).**

## Verdict Response Mapping

| Verdict | Meaning | OPENCLAW Action |
|---------|---------|-----------------|
| `SEAL` | Approved — all F1-F13 satisfied | Execute freely |
| `HOLD_888` | Paused — needs human confirmation | Pause, ask Arif |
| `VOID` | Forbidden — constitutional violation | Do not execute, announce |
| `pending-human-review` | AAA 888_JUDGE gate triggered | Wait for Arif verdict |

## Status Endpoint Rujukan

| Service | Endpoint | Status | Catatan |
|---------|----------|--------|---------|
| arifOS MCP | `arif_judge_deliberate` | **ACTIVE** | Laluan tunggal beroperasi |
| APEX A2A | `http://localhost:3002/tasks` | **DISABLED** | Kredensial digantung |
| AAA Gateway | `http://localhost:3001/a2a/message/send` | **DISABLED** | Kredensial digantung |

**DITEMPA BUKAN DIBERI — Forged, Not Given.**
