# RELEASE NOTES — arifOS v2026.05.22

> **Release date:** 2026-05-22
> **Codename:** Birthday Release — Phases 1-4 Agentic Safety
> **Authority:** F13 SOVEREIGN (Arif)
> **Tag:** `v2026.05.22`

---

## Executive Summary

This release ships the first four phases of agentic safety — a governed execution layer that sits between AI agents and every tool call they attempt. It is the most significant safety upgrade in arifOS history.

**What changes for users:**
- Tool calls are now checked against 13 constitutional floors before execution
- Irreversible actions (send email, delete file, spend money) are paused for human approval
- Scope mismatches are blocked automatically — no API call is made on mismatch
- The NIAT gate detects suspicious communication patterns and escalates to HOLD

---

## Phase 1 — Capability Membrane (F1 AMANAH)

`enforce_capability_membrane()` ensures every action strictly adheres to its one-time, explicitly permitted scope.

- Wired into `arif_forge_execute` and `google_gmail_send`
- Returns **HOLD** when recipient doesn't match `permitted_scope`
- No API call is made on mismatch — fail-closed by design
- SHA-256 body/subject hash matching for email integrity

**Example:**
```python
# Permitted: send to boss@company.com only
result = send_email(to="external@example.com")  # → HOLD (blocked)
```

---

## Phase 2 — NIAT Gate (F5 PEACE, F6 EMPATHY)

New `niat_gate.py` — 12,663 bytes of governed communication safety.

- **SCAR vocabulary:** TIER1 (single-word) + TIER2 (multi-word) suspicious patterns
- **Graduated scoring:** `scar_weight` 0.0–1.0 with context amplifiers
- **Auto-fire conditions:** `mode=="formalize"` or `action_tier in (c3, c4, c5, sovereign)`
- **Verdict:** CONFLICTED → `VerdictOutput(verdict=HOLD)` with `amanah_proof`
- Wired into `judge.py` at line 296+

**Tests:** `tests/runtime/test_niat_gate.py` — 5/5 passing

---

## Phase 3 — MediumShift Auto-Detection (F5 PEACE)

Auto-detects private→formal communication transitions without explicit user instruction.

- Infers from: `private`, `p&c`, `chat`, `whatsapp`, `verbal`, `friend`, `informal`, `personal`, `confidential`
- Does NOT infer from formal contexts — avoids false positives
- Triggers formalization lock when medium shift is detected

---

## Phase 4 — ML Runtime Health (F11 AUTH)

`get_ml_floor_runtime()` now returns clean health telemetry.

- `ml_floors_enabled`, `ml_runtime_ready`, `ml_mode`, `heuristic_fallback_active`
- Resolves KeyError on `/health` endpoint
- Lean Docker container correctly reports heuristic-only mode

---

## Infrastructure & Hygiene

### Entropy Reduction (this release)
- Removed 101 orphaned tracked files (agentzero, apps, transports, workflows.archive, runtime/.archive, _archived, _archived_apps)
- Deleted 2,400 untracked node_modules files (~24.7 MB)
- Added `.antigravitycli/` to `.gitignore`
- Aligned all SOT manifests to 2026-05-22

### Documentation
- Added Problem/Solution hook to README
- Added Hello World Python example
- Added verdict explanation table (SEAL/HOLD/VOID/SABAR)
- Added "Who is this for?" persona section
- Created `docs/ARCHITECTURE_FEDERATION.md` (plain-English topology)
- Added H2 Horizon stub to WEALTH/README.md

---

## Verification

```bash
# NIAT gate tests
pytest tests/runtime/test_niat_gate.py -v  # 5 passed

# Capability membrane
python -c "from arifosmcp.runtime.niat_gate import enforce_capability_membrane; \
           print(enforce_capability_membrane('tool', {'to':'x'}, {'tool':'tool','to':'y'}))"  # False

# Full suite
pytest tests/ -q --tb=short  # ~1939 passed
```

---

## Federation Compatibility

| Organ | Minimum Version | Status |
|-------|----------------|--------|
| arifOS | `2026.05.22` | ✅ This release |
| AAA | `v55.3.0+` | ✅ Verified |
| A-FORGE | `latest` | ✅ Compatible |
| GEOX | `7d662d6+` | ✅ Compatible |
| WEALTH | `latest` | ⚠️ H2 horizon — thermodynamic capital stubbed |
| WELL | `latest` | ✅ Compatible |

---

## Upgrade

```bash
pip install --upgrade arifos
```

Docker:
```bash
docker pull ghcr.io/ariffazil/arifos:2026.05.22
```

---

*DITEMPA BUKAN DIBERI — Intelligence is forged, not given.*
*999 SEAL ALIVE*
