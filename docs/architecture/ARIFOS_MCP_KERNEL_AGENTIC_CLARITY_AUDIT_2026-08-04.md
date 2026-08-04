# arifOS MCP Kernel — Agentic Clarity Audit

**Session:** `SEAL-00c789d4a0174c93`  
**Actor:** ARIF (SOVEREIGN)  
**Date:** 2026-08-04  
**Auditor:** grok-build (FI-007)  
**Scope:** 8 public kernel verbs — discoverability, mode truth, chaining, authority  

**Live substrate at init:** DEGRADED (`deployment_drift`, source≠built) · load_1m ~11.6 · mutation_allowed=false  

---

## Executive verdict

**Bones excellent. Docs drifted from runtime.** Agents fail predictably on empty manifests, phantom modes, and dead next-tool pointers — not on missing capability.

| # | Defect | Severity | Status after this patch |
|---|--------|----------|-------------------------|
| P0-A | `arif_route` / `arif_memory` empty manifests (`TOOL_CHARTER` keyed by legacy names) | P0 | **FIXED** — live keys + full grammar |
| P0-B | Phantom modes (manifest docs modes live schema rejects) | P0 | **FIXED** for 8 public tools |
| P0-C | Ghost modes (live, undocumented) | P0 | **FIXED** for 8 public tools |
| P1-A | Dead `next_recommended_tools` (`arif_fetch`, `arif_critique`, …) | P1 | **FIXED** + remap footer |
| P1-A′ | Live init `next_tool: arif_triage` (not a tool) | P1 | **FIXED** → `arif_observe` |
| P1-B | FORGE stage_code `010` vs title `777` | P1 | **FIXED** → `777` |
| P1-C | `canonical_order: []` empty | P1 | **FIXED** — stamped on all entries |
| P2-A | Dual risk scales | P2 | **DOCUMENTED** — `risk_scale_map` + passport authoritative |
| P2-B | SCT / `session_token` undocumented | P2 | **FIXED** — outputs + carries_forward |
| P2-C | No verdict-response contract | P2 | **FIXED** — `VERDICT_RESPONSE_CONTRACT` on every entry |
| P2-D | `idempotentHint: true` on init | P2 | **FIXED** → false |
| P2-E | Degraded / 5xx behavior undocumented | P2 | **FIXED** — `FAILURE_MODES_KERNEL` |

---

## Root cause (P0-A)

```python
# runtime/tools.py registration
manifest = TOOL_CHARTER.get(name, {})  # name = arif_route | arif_memory
```

Charter only had `arif_kernel_route` and `arif_memory_recall` → `{}` on the public surface.

---

## Mode-drift matrix (pre-patch) → post-patch

Live schema (MCP input enums) is truth. Manifest modes now match:

| Tool | Live modes (post-align) |
|------|-------------------------|
| arif_init | init, light, resume, validate, canary, preflight, triage, epoch_open, epoch_seal, opt_out, opt_out_profiling |
| arif_observe | search, fetch, hybrid_discovery, ingest, compass, atlas, entropy_dS, vitals |
| arif_think | reason, reflect, verify, axioms, plan, plan_review, plan_approve, refactor_plan, metabolize, simulate, wonder, atlas |
| arif_route | route, bridge |
| arif_memory | recall, inspect, attest, remember, promote, revise, forget, audit |
| arif_judge | intercept, judge, validate, hold, escalate |
| arif_forge | engineer, query, write, generate, commit, recall, dry_run |
| arif_seal | seal, verify, ledger, changelog, audit, session_close |

**Phantoms removed:** think `critique`; judge `compare/history/explain`; seal `chain/list`; forge `rollback` required_when.

---

## Canonical pipeline (agents)

```
arif_init → arif_observe → arif_think → arif_route → arif_memory
         → arif_judge → arif_forge → arif_seal
```

## Verdict response contract (agents)

| Verdict | Agent action |
|---------|--------------|
| SEAL | Proceed to next stage |
| HOLD | Stop; escalate F13 human |
| SABAR | Backoff / retry after degraded clears |
| VOID | Abandon branch |
| PARTIAL_PROCEED | OBSERVE/THINK only; no forge/seal |

## Failure modes (agents)

| Condition | Action |
|-----------|--------|
| HTTP 5xx | Backoff ≥60s, retry once → SABAR if persists |
| deployment_drift | HOLD mutation; observe/think only |
| empty_manifest | Trust live mode enum only |

---

## Files changed

| Path | Change |
|------|--------|
| `arifosmcp/tool_charter.py` | Live keys, full route/memory manifests, mode reconcile, contracts, dead-pointer remap |
| `arifosmcp/tools/session.py` | `next_tool` never emits `arif_triage` |
| `arifosmcp/constitutional_map.py` | `arif_init` idempotentHint=false |

## Deploy note

Init reported `deployment_drift` (source ≠ built). **Source patched.** Runtime still old until:

```bash
# After tests green — T2 deploy
make -C /root/arifOS deploy-local   # or rsync → systemctl restart arifos
```

Do not claim live MCP meta updated until post-deploy tools/list shows non-empty `arifos_manifest` for route/memory.

---

## Epistemic labels

| Claim | Label |
|-------|-------|
| Empty manifests from key mismatch | OBS |
| Mode matrix vs live MCP schema | OBS |
| Agents fail on phantom modes | DER (~0.9) |
| Priority ranking P0/P1/P2 | INT |
| 502 / load under prior session | OBS (prior agent) |

---

*DITEMPA BUKAN DIBERI — documentation forged to match runtime, not invented.*
